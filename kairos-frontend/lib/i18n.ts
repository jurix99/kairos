// Traductions et formatage international
export const translations = {
  en: {
    days: {
      long: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
      short: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    },
    months: {
      long: ["January", "February", "March", "April", "May", "June", 
             "July", "August", "September", "October", "November", "December"],
      short: ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    }
  },
  fr: {
    days: {
      long: ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
      short: ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    },
    months: {
      long: ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
             "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"],
      short: ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
              "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    }
  }
}

export const formatTime = (date: Date, format: '12h' | '24h', language: string = 'en'): string => {
  if (format === '24h') {
    return date.toLocaleTimeString(language === 'fr' ? 'fr-FR' : 'en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  } else {
    return date.toLocaleTimeString(language === 'fr' ? 'fr-FR' : 'en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }
}

export const formatHour = (hour: number, format: '12h' | '24h'): string => {
  if (format === '24h') {
    return `${hour.toString().padStart(2, '0')}:00`
  } else {
    if (hour === 0) return "12:00 AM"
    if (hour < 12) return `${hour}:00 AM`
    if (hour === 12) return "12:00 PM"
    return `${hour - 12}:00 PM`
  }
}

export const getDayName = (dayIndex: number, language: string = 'en', short: boolean = false): string => {
  const lang = language as keyof typeof translations
  const days = short ? translations[lang]?.days.short : translations[lang]?.days.long
  return days?.[dayIndex] || translations.en.days.long[dayIndex]
}

export const getMonthName = (monthIndex: number, language: string = 'en', short: boolean = false): string => {
  const lang = language as keyof typeof translations
  const months = short ? translations[lang]?.months.short : translations[lang]?.months.long
  return months?.[monthIndex] || translations.en.months.long[monthIndex]
}

