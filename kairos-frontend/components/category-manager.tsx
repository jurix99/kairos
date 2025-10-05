"use client"

import { useState, useEffect } from "react"
import { Plus, Edit, Trash2, Save, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ColorPicker } from "@/components/ui/color-picker"
import { Badge } from "@/components/ui/badge"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog"
import { apiClient, type Category } from "@/lib/api"
import { getNextAvailableColor } from "@/lib/colors"
import { cn } from "@/lib/utils"

interface CategoryManagerProps {
  categories: Category[]
  onCategoriesChange: () => void
}

interface CategoryFormData {
  name: string
  color: string
  description?: string
}

export function CategoryManager({ categories, onCategoriesChange }: CategoryManagerProps) {
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<CategoryFormData>({
    name: '',
    color: '',
    description: ''
  })
  const [isLoading, setIsLoading] = useState(false)

  // Reset form when starting to create a new category
  const startCreating = () => {
    const usedColors = categories.map(cat => cat.color)
    const nextColor = getNextAvailableColor(usedColors)
    
    setFormData({
      name: '',
      color: nextColor,
      description: ''
    })
    setIsCreating(true)
    setEditingId(null)
  }

  // Start editing an existing category
  const startEditing = (category: Category) => {
    setFormData({
      name: category.name,
      color: category.color,
      description: category.description || ''
    })
    setEditingId(category.id)
    setIsCreating(false)
  }

  // Cancel editing/creating
  const cancelEditing = () => {
    setIsCreating(false)
    setEditingId(null)
    setFormData({ name: '', color: '', description: '' })
  }

  // Save category (create or update)
  const saveCategory = async () => {
    if (!formData.name.trim()) {
      alert('Le nom de la catégorie est requis')
      return
    }

    setIsLoading(true)
    try {
      const categoryData = {
        name: formData.name.trim(),
        color: formData.color, // Use color (will be converted to color_code in API client)
        description: formData.description?.trim() || undefined
      }

      if (editingId) {
        // Update existing category
        await apiClient.updateCategory(editingId, categoryData)
      } else {
        // Create new category
        await apiClient.createCategory(categoryData)
      }

      onCategoriesChange()
      cancelEditing()
    } catch (error) {
      console.error('Failed to save category:', error)
      alert('Erreur lors de la sauvegarde de la catégorie')
    } finally {
      setIsLoading(false)
    }
  }

  // Delete category
  const deleteCategory = async (categoryId: string) => {
    setIsLoading(true)
    try {
      await apiClient.deleteCategory(categoryId)
      onCategoriesChange()
    } catch (error) {
      console.error('Failed to delete category:', error)
      alert('Erreur lors de la suppression de la catégorie')
    } finally {
      setIsLoading(false)
    }
  }

  const updateFormData = (field: keyof CategoryFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Gestion des Catégories</CardTitle>
            <CardDescription>
              Créez et personnalisez vos catégories d'événements
            </CardDescription>
          </div>
          {!isCreating && !editingId && (
            <Button onClick={startCreating} size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Nouvelle catégorie
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        
        {/* Form for creating/editing category */}
        {(isCreating || editingId) && (
          <Card className="border-dashed">
            <CardContent className="p-4">
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="category-name">Nom de la catégorie *</Label>
                    <Input
                      id="category-name"
                      value={formData.name}
                      onChange={(e) => updateFormData('name', e.target.value)}
                      placeholder="ex: Travail, Personnel, Sport..."
                    />
                  </div>
                  <ColorPicker
                    color={formData.color}
                    onColorChange={(color) => updateFormData('color', color)}
                    label="Couleur"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="category-description">Description (optionnel)</Label>
                  <Input
                    id="category-description"
                    value={formData.description}
                    onChange={(e) => updateFormData('description', e.target.value)}
                    placeholder="Description de la catégorie..."
                  />
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    onClick={saveCategory}
                    disabled={isLoading || !formData.name.trim()}
                    size="sm"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {isLoading ? 'Sauvegarde...' : editingId ? 'Modifier' : 'Créer'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={cancelEditing}
                    disabled={isLoading}
                    size="sm"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Annuler
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* List of existing categories */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Catégories existantes ({categories.length})</Label>
          {categories.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Aucune catégorie créée. Commencez par créer votre première catégorie !
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-2">
              {categories.map((category) => (
                <div
                  key={category.id}
                  className={cn(
                    "flex items-center justify-between p-3 rounded-lg border transition-colors",
                    editingId === category.id ? "border-primary bg-accent/50" : "border-border hover:bg-accent/30"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className="w-4 h-4 rounded-full flex-shrink-0"
                      style={{ backgroundColor: category.color }}
                    />
                    <div className="flex-1">
                      <div className="font-medium">{category.name}</div>
                      {category.description && (
                        <div className="text-sm text-muted-foreground">
                          {category.description}
                        </div>
                      )}
                    </div>
                    <Badge
                      variant="outline"
                      className="text-xs"
                      style={{
                        borderColor: category.color,
                        color: category.color,
                      }}
                    >
                      {category.color}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => startEditing(category)}
                      disabled={isLoading || editingId === category.id}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          disabled={isLoading}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Supprimer la catégorie</AlertDialogTitle>
                          <AlertDialogDescription>
                            Êtes-vous sûr de vouloir supprimer la catégorie "{category.name}" ?
                            Cette action ne peut pas être annulée et affectera tous les événements associés.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Annuler</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => deleteCategory(category.id)}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                          >
                            Supprimer
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}