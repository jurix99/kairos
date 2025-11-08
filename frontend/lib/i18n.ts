/**
 * Internationalization utilities for date and time formatting
 */

/**
 * Format time based on locale and format preference
 */
export function formatTime(
  date: Date,
  format: '12h' | '24h' = '24h',
  locale: string = 'en'
): string {
  const options: Intl.DateTimeFormatOptions = {
    hour: 'numeric',
    minute: '2-digit',
    hour12: format === '12h'
  }

  return new Intl.DateTimeFormat(locale, options).format(date)
}

/**
 * Format hour for display (e.g., "09:00", "9:00 AM")
 */
export function formatHour(
  hour: number,
  format: '12h' | '24h' = '24h',
  locale: string = 'en'
): string {
  const date = new Date()
  date.setHours(hour, 0, 0, 0)
  return formatTime(date, format, locale)
}

/**
 * Get localized day name
 */
export function getDayName(
  dayIndex: number,
  locale: string = 'en',
  format: 'long' | 'short' | 'narrow' = 'long'
): string {
  const date = new Date()
  // Set to a known week (e.g., Jan 4, 2021 is a Monday)
  date.setDate(4 + dayIndex)
  date.setMonth(0)
  date.setFullYear(2021)

  const options: Intl.DateTimeFormatOptions = {
    weekday: format
  }

  return new Intl.DateTimeFormat(locale, options).format(date)
}

/**
 * Get localized month name
 */
export function getMonthName(
  monthIndex: number,
  locale: string = 'en',
  format: 'long' | 'short' | 'narrow' = 'long'
): string {
  const date = new Date()
  date.setMonth(monthIndex)
  date.setDate(1)

  const options: Intl.DateTimeFormatOptions = {
    month: format
  }

  return new Intl.DateTimeFormat(locale, options).format(date)
}

/**
 * Format a full date
 */
export function formatDate(
  date: Date,
  locale: string = 'en',
  options?: Intl.DateTimeFormatOptions
): string {
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options
  }

  return new Intl.DateTimeFormat(locale, defaultOptions).format(date)
}

/**
 * Format date and time together
 */
export function formatDateTime(
  date: Date,
  timeFormat: '12h' | '24h' = '24h',
  locale: string = 'en'
): string {
  const dateStr = formatDate(date, locale, { month: 'short', day: 'numeric' })
  const timeStr = formatTime(date, timeFormat, locale)
  return `${dateStr}, ${timeStr}`
}

/**
 * Get relative time string (e.g., "in 2 hours", "3 days ago")
 */
export function getRelativeTime(
  date: Date,
  locale: string = 'en'
): string {
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })

  if (Math.abs(diffDays) >= 1) {
    return rtf.format(diffDays, 'day')
  } else if (Math.abs(diffHours) >= 1) {
    return rtf.format(diffHours, 'hour')
  } else if (Math.abs(diffMins) >= 1) {
    return rtf.format(diffMins, 'minute')
  } else {
    return rtf.format(diffSecs, 'second')
  }
}
