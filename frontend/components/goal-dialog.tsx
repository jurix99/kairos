"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { apiClient } from "@/lib/api"
import type { Goal } from "@/lib/api"

interface GoalDialogProps {
  goal?: Goal | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onGoalSaved: () => void
}

export function GoalDialog({ goal, open, onOpenChange, onGoalSaved }: GoalDialogProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    target_date: "",
    priority: "medium" as "low" | "medium" | "high",
    status: "active" as "active" | "completed" | "paused" | "cancelled",
    category: "none" as string,
    strategy: "",
    success_criteria: "",
    current_value: "",
    target_value: "",
    unit: "",
  })
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (goal) {
      setFormData({
        title: goal.title,
        description: goal.description || "",
        target_date: goal.target_date ? new Date(goal.target_date).toISOString().split('T')[0] : "",
        priority: goal.priority,
        status: goal.status,
        category: goal.category || "none",
        strategy: goal.strategy || "",
        success_criteria: goal.success_criteria || "",
        current_value: goal.current_value || "",
        target_value: goal.target_value || "",
        unit: goal.unit || "",
      })
    } else {
      setFormData({
        title: "",
        description: "",
        target_date: "",
        priority: "medium",
        status: "active",
        category: "none",
        strategy: "",
        success_criteria: "",
        current_value: "",
        target_value: "",
        unit: "",
      })
    }
  }, [goal, open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const goalData = {
        ...formData,
        target_date: formData.target_date ? new Date(formData.target_date + 'T00:00:00').toISOString() : undefined,
        category: formData.category === "none" || !formData.category ? undefined : formData.category,
      }

      if (goal) {
        await apiClient.updateGoal(goal.id, goalData)
      } else {
        await apiClient.createGoal(goalData)
      }

      onGoalSaved()
    } catch (error) {
      console.error("Failed to save goal:", error)
      alert("Erreur lors de la sauvegarde de l'objectif")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!goal) return
    
    if (confirm("Êtes-vous sûr de vouloir supprimer cet objectif ?")) {
      setIsLoading(true)
      try {
        await apiClient.deleteGoal(goal.id)
        onGoalSaved()
      } catch (error) {
        console.error("Failed to delete goal:", error)
        alert("Erreur lors de la suppression de l'objectif")
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {goal ? "Modifier l'objectif" : "Nouvel objectif"}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <Label htmlFor="title">Titre *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="ex: Courir un marathon"
                required
              />
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Description détaillée de votre objectif..."
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="target_date">Date cible</Label>
              <Input
                id="target_date"
                type="date"
                value={formData.target_date}
                onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
              />
            </div>

            <div>
              <Label htmlFor="category">Catégorie</Label>
              <Select value={formData.category} onValueChange={(value) => setFormData({ ...formData, category: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Choisir une catégorie" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Aucune catégorie</SelectItem>
                  <SelectItem value="sport">Sport</SelectItem>
                  <SelectItem value="career">Carrière</SelectItem>
                  <SelectItem value="health">Santé</SelectItem>
                  <SelectItem value="education">Éducation</SelectItem>
                  <SelectItem value="personal">Personnel</SelectItem>
                  <SelectItem value="financial">Financier</SelectItem>
                  <SelectItem value="relationships">Relations</SelectItem>
                  <SelectItem value="hobbies">Loisirs</SelectItem>
                  <SelectItem value="other">Autre</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="priority">Priorité</Label>
              <Select value={formData.priority} onValueChange={(value: any) => setFormData({ ...formData, priority: value })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Basse</SelectItem>
                  <SelectItem value="medium">Moyenne</SelectItem>
                  <SelectItem value="high">Haute</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="status">Statut</Label>
              <Select value={formData.status} onValueChange={(value: any) => setFormData({ ...formData, status: value })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Actif</SelectItem>
                  <SelectItem value="completed">Terminé</SelectItem>
                  <SelectItem value="paused">En pause</SelectItem>
                  <SelectItem value="cancelled">Annulé</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="strategy">Stratégie</Label>
              <Textarea
                id="strategy"
                value={formData.strategy}
                onChange={(e) => setFormData({ ...formData, strategy: e.target.value })}
                placeholder="Décrivez votre plan d'action et stratégie pour atteindre cet objectif..."
                rows={3}
              />
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="success_criteria">Critères de réussite</Label>
              <Textarea
                id="success_criteria"
                value={formData.success_criteria}
                onChange={(e) => setFormData({ ...formData, success_criteria: e.target.value })}
                placeholder="Comment saurez-vous que vous avez atteint votre objectif ?"
                rows={2}
              />
            </div>

            <div>
              <Label htmlFor="current_value">Valeur actuelle</Label>
              <Input
                id="current_value"
                value={formData.current_value}
                onChange={(e) => setFormData({ ...formData, current_value: e.target.value })}
                placeholder="ex: 5km, 2h/jour"
              />
            </div>

            <div>
              <Label htmlFor="target_value">Valeur cible</Label>
              <Input
                id="target_value"
                value={formData.target_value}
                onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                placeholder="ex: 42km, 4h/jour"
              />
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="unit">Unité de mesure</Label>
              <Input
                id="unit"
                value={formData.unit}
                onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                placeholder="ex: km, heures, euros, %"
              />
            </div>
          </div>

          <div className="flex justify-between pt-4">
            <div>
              {goal && (
                <Button 
                  type="button" 
                  variant="destructive" 
                  onClick={handleDelete}
                  disabled={isLoading}
                >
                  Supprimer
                </Button>
              )}
            </div>
            
            <div className="flex gap-2">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => onOpenChange(false)}
                disabled={isLoading}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={isLoading || !formData.title.trim()}>
                {isLoading ? "Sauvegarde..." : goal ? "Mettre à jour" : "Créer"}
              </Button>
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
