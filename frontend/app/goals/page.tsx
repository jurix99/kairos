"use client"

import { useState, useEffect } from "react"
import { Plus, Target, Calendar, TrendingUp, CheckCircle, Clock, PauseCircle, XCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { SiteHeader } from "@/components/site-header"
import { useAuth } from "@/contexts/auth-context"
import { apiClient } from "@/lib/api"
import type { Goal } from "@/lib/api"
import { GoalDialog } from "@/components/goal-dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function GoalsPage() {
  const { user } = useAuth()
  const [goals, setGoals] = useState<Goal[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    loadData()
  }, [statusFilter, categoryFilter])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const [goalsData, statsData] = await Promise.all([
        apiClient.getGoals(
          statusFilter !== "all" ? statusFilter as any : undefined,
          categoryFilter !== "all" ? categoryFilter : undefined
        ),
        apiClient.getGoalStatistics()
      ])
      setGoals(goalsData)
      setStats(statsData)
    } catch (error) {
      console.error("Failed to load goals:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateGoal = () => {
    setSelectedGoal(null)
    setDialogOpen(true)
  }

  const handleEditGoal = (goal: Goal) => {
    setSelectedGoal(goal)
    setDialogOpen(true)
  }

  const handleGoalSaved = () => {
    loadData()
    setDialogOpen(false)
    setSelectedGoal(null)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'active':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'paused':
        return <PauseCircle className="h-4 w-4 text-yellow-500" />
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Target className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 hover:bg-green-200'
      case 'active':
        return 'bg-blue-100 text-blue-800 hover:bg-blue-200'
      case 'paused':
        return 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
      case 'cancelled':
        return 'bg-red-100 text-red-800 hover:bg-red-200'
      default:
        return 'bg-gray-100 text-gray-800 hover:bg-gray-200'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Aucune date cible"
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
      </div>
    )
  }

  return (
    <>
      <SiteHeader 
        user={user}
        controls={
          <div className="flex items-center gap-4">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Filtrer par statut" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les statuts</SelectItem>
                <SelectItem value="active">Actif</SelectItem>
                <SelectItem value="completed">Terminé</SelectItem>
                <SelectItem value="paused">En pause</SelectItem>
                <SelectItem value="cancelled">Annulé</SelectItem>
              </SelectContent>
            </Select>

            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Filtrer par catégorie" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes les catégories</SelectItem>
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

            <Button onClick={handleCreateGoal}>
              <Plus className="h-4 w-4 mr-2" />
              Nouvel objectif
            </Button>
          </div>
        }
      />

      <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_goals}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Actifs</CardTitle>
                <Clock className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.active_goals}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Terminés</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.completed_goals}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Taux de réussite</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{Math.round(stats.completion_rate)}%</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Goals List */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            </div>
          ) : goals.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Target className="h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Aucun objectif trouvé
                </h3>
                <p className="text-gray-600 text-center mb-4">
                  Commencez par créer votre premier objectif et définissez une stratégie pour l'atteindre.
                </p>
                <Button onClick={handleCreateGoal}>
                  <Plus className="h-4 w-4 mr-2" />
                  Créer un objectif
                </Button>
              </CardContent>
            </Card>
          ) : (
            goals.map((goal) => (
              <Card key={goal.id} className="cursor-pointer hover:shadow-md transition-shadow" 
                    onClick={() => handleEditGoal(goal)}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getStatusIcon(goal.status)}
                        <CardTitle className="text-lg">{goal.title}</CardTitle>
                        <Badge className={getStatusColor(goal.status)}>
                          {goal.status === 'active' ? 'Actif' : 
                           goal.status === 'completed' ? 'Terminé' :
                           goal.status === 'paused' ? 'En pause' : 'Annulé'}
                        </Badge>
                        <Badge className={getPriorityColor(goal.priority)}>
                          {goal.priority === 'high' ? 'Haute' : 
                           goal.priority === 'medium' ? 'Moyenne' : 'Basse'}
                        </Badge>
                        {goal.category && (
                          <Badge variant="outline">
                            {goal.category === 'sport' ? 'Sport' :
                             goal.category === 'career' ? 'Carrière' :
                             goal.category === 'health' ? 'Santé' :
                             goal.category === 'education' ? 'Éducation' :
                             goal.category === 'personal' ? 'Personnel' :
                             goal.category === 'financial' ? 'Financier' :
                             goal.category === 'relationships' ? 'Relations' :
                             goal.category === 'hobbies' ? 'Loisirs' : 'Autre'}
                          </Badge>
                        )}
                      </div>
                      
                      {goal.description && (
                        <p className="text-gray-600 mb-3">{goal.description}</p>
                      )}
                      
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {formatDate(goal.target_date)}
                        </div>
                        
                        {goal.current_value && goal.target_value && (
                          <div className="flex items-center gap-1">
                            <TrendingUp className="h-4 w-4" />
                            {goal.current_value} / {goal.target_value} {goal.unit}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                
                {(goal.strategy || goal.success_criteria) && (
                  <CardContent className="pt-0">
                    {goal.strategy && (
                      <div className="mb-2">
                        <h4 className="font-medium text-sm text-gray-700 mb-1">Stratégie :</h4>
                        <p className="text-sm text-gray-600">{goal.strategy}</p>
                      </div>
                    )}
                    
                    {goal.success_criteria && (
                      <div>
                        <h4 className="font-medium text-sm text-gray-700 mb-1">Critères de réussite :</h4>
                        <p className="text-sm text-gray-600">{goal.success_criteria}</p>
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Goal Creation/Edit Dialog */}
      <GoalDialog
        goal={selectedGoal}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onGoalSaved={handleGoalSaved}
      />
    </>
  )
}

