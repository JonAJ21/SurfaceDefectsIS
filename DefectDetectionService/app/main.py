from utils.detection_service import DetectionService
import asyncio
from loguru import logger

async def main():
    service = DetectionService()
    await service.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")