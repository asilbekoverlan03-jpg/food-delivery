import { CURRENCY } from '../config'

/**
 * Форматирует цену: 1250.00 → "1 250 сом", 300 → "300 сом"
 * Пробел как разделитель тысяч, без дробной части если она нулевая.
 */
export function formatPrice(value) {
  const num = parseFloat(value)
  if (isNaN(num)) return `0 ${CURRENCY}`
  // если дробная часть ненулевая — показываем 2 знака, иначе целое
  const formatted = Number.isInteger(num)
    ? num.toLocaleString('ru-RU')
    : num.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return `${formatted} ${CURRENCY}`
}
