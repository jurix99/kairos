// Palette de couleurs prédéfinies pour les catégories
export const DEFAULT_CATEGORY_COLORS = [
  "#6366f1", // Indigo
  "#8b5cf6", // Violet  
  "#06b6d4", // Cyan
  "#10b981", // Emerald
  "#f59e0b", // Amber
  "#ef4444", // Red
  "#ec4899", // Pink
  "#84cc16", // Lime
  "#f97316", // Orange
  "#6b7280", // Gray
  "#14b8a6", // Teal
  "#a855f7", // Purple
  "#0ea5e9", // Blue
  "#22c55e", // Green
  "#eab308", // Yellow
  "#dc2626", // Red-600
  "#db2777", // Pink-600
  "#65a30d", // Lime-600
  "#ea580c", // Orange-600
  "#374151", // Gray-700
] as const

// Fonction pour obtenir la prochaine couleur disponible
export function getNextAvailableColor(usedColors: string[]): string {
  const availableColors = DEFAULT_CATEGORY_COLORS.filter(
    color => !usedColors.includes(color)
  )
  
  if (availableColors.length === 0) {
    // Si toutes les couleurs sont utilisées, on génère une couleur aléatoire
    return generateRandomColor()
  }
  
  return availableColors[0]
}

// Fonction pour générer une couleur aléatoire en hex
export function generateRandomColor(): string {
  const letters = '0123456789ABCDEF'
  let color = '#'
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)]
  }
  return color
}

// Fonction pour vérifier si une couleur est valide (format hex)
export function isValidHexColor(color: string): boolean {
  return /^#[0-9A-F]{6}$/i.test(color)
}

// Fonction pour obtenir une couleur contrastée (texte) pour une couleur de fond
export function getContrastColor(backgroundColor: string): string {
  // Convertir la couleur hex en RGB
  const hex = backgroundColor.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)
  
  // Calculer la luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  
  // Retourner noir ou blanc selon la luminance
  return luminance > 0.5 ? '#000000' : '#ffffff'
}
