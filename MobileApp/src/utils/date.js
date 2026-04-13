/**
 * Конвертирует дату из БД (UTC) в локальное время пользователя
 * @param {string} dateStr - ISO строка даты от сервера
 * @returns {string} Дата и время в часовом поясе устройства
 */
export const formatDate = (dateStr) => {
  if (!dateStr) return 'Неизвестно';
  
  // Если строка не содержит указания часового пояса, явно помечаем её как UTC
  const hasTimezoneInfo = dateStr.endsWith('Z') || dateStr.includes('+') || dateStr.match(/T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2}/);
  const normalizedStr = hasTimezoneInfo ? dateStr : `${dateStr}Z`;
  
  const date = new Date(normalizedStr);
  if (isNaN(date.getTime())) return 'Неизвестно';
  
  // toLocaleString автоматически применяет часовой пояс и локаль устройства
  return date.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};