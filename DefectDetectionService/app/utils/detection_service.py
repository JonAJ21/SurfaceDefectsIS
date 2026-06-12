import asyncio
import cv2
import numpy as np
import redis.asyncio as redis
import httpx
from ultralytics import YOLO
from typing import Optional, Dict, Any
import logging
from utils.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DetectionService:
    def __init__(self):
        self.model = None
        self.redis_client = None
        self.http_client = None
        self.access_token = None
        self.consumer_name = settings.consumer_name

    @staticmethod
    def resize_image(img_bgr: np.ndarray) -> np.ndarray:
        return cv2.resize(img_bgr, (settings.img_size, settings.img_size), 
                         interpolation=cv2.INTER_LINEAR)

    @staticmethod
    def apply_clahe_bgr(img_bgr: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_channel = clahe.apply(l_channel)
        enhanced_lab = cv2.merge([l_channel, a_channel, b_channel])
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    @staticmethod
    def denoise_image(img_bgr: np.ndarray) -> np.ndarray:
        return cv2.bilateralFilter(img_bgr, d=6, sigmaColor=40, sigmaSpace=40)

    def preprocess(self, img_bgr: np.ndarray) -> np.ndarray:
        resized = self.resize_image(img_bgr)
        enhanced = self.apply_clahe_bgr(resized)
        denoised = self.denoise_image(enhanced)
        return denoised

    def load_model(self) -> None:
        logger.info(f"Loading model from {settings.model_path}")
        self.model = YOLO(settings.model_path)
        logger.info("Model loaded successfully")

    async def authenticate(self) -> bool:
        try:
            async with self.http_client as client:
                response = await client.post(
                    f"{settings.auth_service_url}/v1/service/login",
                    json={
                        "service_name": settings.service_name,
                        "secret": settings.service_secret
                    }
                )
                if response.status_code == 200:
                    self.access_token = response.json().get("access_token")
                    logger.info("Authentication successful")
                    return True
                else:
                    logger.error(f"Authentication failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
        return False

    async def init_redis(self) -> None:
        self.redis_client = await redis.from_url(settings.redis_url)
        try:
            await self.redis_client.xgroup_create(
                settings.redis_stream,
                settings.consumer_group,
                id="0",
                mkstream=True
            )
            logger.info(f"Consumer group {settings.consumer_group} created")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group {settings.consumer_group} already exists")
            else:
                logger.warning(f"Redis init warning: {e}")

    async def read_messages(self):
        messages = await self.redis_client.xreadgroup(
            groupname=settings.consumer_group,
            consumername=self.consumer_name,
            streams={settings.redis_stream: ">"},
            count=settings.batch_size,
            block=settings.block_ms,
        )
        return messages

    async def ack_message(self, stream: str, message_id: str) -> None:
        await self.redis_client.xack(stream, settings.consumer_group, message_id)
        logger.debug(f"Acknowledged message {message_id}")

    async def load_image_from_minio(self, bucket: str, object_path: str) -> Optional[np.ndarray]:
        try:
            pass
        except Exception as e:
            logger.error(f"Failed to load image from MinIO: {e}")
            return None

    def detect_defects(self, image: np.ndarray) -> Dict[str, Any]:
        preprocessed = self.preprocess(image)
        results = self.model(preprocessed, verbose=False)[0]
        
        detected = []
        for box in results.boxes:
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            
            if confidence >= settings.confidence_threshold:
                detected.append({
                    "class_id": class_id,
                    "class_name": self.model.names[class_id],
                    "confidence": confidence,
                })
        
        max_conf = max([d["confidence"] for d in detected]) if detected else 0.0
        
        return {
            "detected": len(detected) > 0,
            "defects": detected,
            "max_confidence": max_conf
        }

    async def moderate_defect(self, defect_id: int, status: str, detected_type: Optional[str] = None) -> bool:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{settings.defects_service_url}/v1/defects/{defect_id}/moderate"
        params = {"status": status}
        if detected_type:
            params["detected_type"] = detected_type
        
        try:
            async with self.http_client as client:
                response = await client.patch(url, params=params, headers=headers)
                if response.status_code == 200:
                    logger.info(f"Defect {defect_id} -> {status}")
                    return True
                else:
                    logger.error(f"Failed to moderate defect {defect_id}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error moderating defect {defect_id}: {e}")
        return False

    async def process_message(self, stream: str, message_id: str, data: Dict) -> None:
        try:
            defect_id = int(data.get(b"defect_id", 0))
            photo_path = data.get(b"photo_path", b"").decode()
            
            if not defect_id or not photo_path:
                logger.warning(f"Invalid message data: {data}")
                await self.ack_message(stream, message_id)
                return
            
            logger.info(f"Processing defect {defect_id}, photo: {photo_path}")
            
            image = await self.load_image_from_minio("defects", photo_path)
            if image is None:
                await self.ack_message(stream, message_id)
                return
            
            result = self.detect_defects(image)
            
            if result["detected"] and result["max_confidence"] >= settings.confidence_threshold:
                detected_type = result["defects"][0]["class_name"]
                await self.moderate_defect(defect_id, "approved", detected_type)
            else:
                logger.info(f"Defect {defect_id} remains pending (confidence: {result['max_confidence']:.2f})")
            
            await self.ack_message(stream, message_id)
            
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")

    async def run(self) -> None:
        self.load_model()
        await self.init_redis()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            self.http_client = client
            
            if not await self.authenticate():
                logger.error("Authentication failed, exiting")
                return
            
            logger.info(f"Service {self.consumer_name} started, waiting for messages...")
            
            while True:
                try:
                    messages = await self.read_messages()
                    
                    if not messages:
                        continue
                    
                    for stream, stream_messages in messages:
                        for message_id, data in stream_messages:
                            await self.process_message(stream, message_id, data)
                            
                except asyncio.CancelledError:
                    logger.info("Service stopped")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {e}")
                    await asyncio.sleep(1)
