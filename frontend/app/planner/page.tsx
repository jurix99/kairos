"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { SiteHeader } from "@/components/site-header"
import { useAuth } from "@/contexts/auth-context"
import { 
  IconSparkles, 
  IconTarget, 
  IconBulb, 
  IconTrendingUp,
  IconCalendarEvent,
  IconListCheck
} from "@tabler/icons-react"
import { Bot, AlertCircle, CheckCircle2, Loader2 } from "lucide-react"
import { 
  apiClient, 
  OrchestratedPlanResponse,
  AgentType,
  NeedType 
} from "@/lib/api"
import { useRouter } from "next/navigation"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export default function PlannerPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [plan, setPlan] = useState<OrchestratedPlanResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [streamingStatus, setStreamingStatus] = useState<string>("")
  const [classification, setClassification] = useState<any>(null)
  const [agentResponses, setAgentResponses] = useState<any[]>([])
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const handleCreatePlan = async () => {
    if (!input.trim() || isLoading) return

    setIsLoading(true)
    setError(null)
    setPlan(null)
    setClassification(null)
    setAgentResponses([])
    setCurrentAgent(null)
    setStreamingStatus("Initialisation...")

    try {
      const user = localStorage.getItem('kairos_user');
      const eventSource = new EventSource(
        `${API_BASE_URL || 'http://localhost:8080'}/api/orchestration/plan/stream`,
        {
          headers: user ? { 'Authorization': `Bearer ${user}` } : {}
        } as any
      )

      // Envoyer la requête en POST via fetch d'abord
      const response = await fetch(`${API_BASE_URL || 'http://localhost:8080'}/api/orchestration/plan/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': user ? `Bearer ${user}` : '',
        },
        body: JSON.stringify({
          user_input: input.trim(),
          create_goals: true,
          include_calendar_integration: true,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create plan')
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))

            switch (data.type) {
              case 'status':
                setStreamingStatus(data.message)
                break

              case 'classification':
                setClassification(data.data)
                setStreamingStatus("Classification terminée !")
                break

              case 'agent_start':
                setCurrentAgent(data.agent_type)
                setStreamingStatus(`Consultation de l'expert en cours...`)
                break

              case 'agent_complete':
                setAgentResponses(prev => [...prev, data.data])
                setCurrentAgent(null)
                break

              case 'complete':
                setPlan(data.data)
                setStreamingStatus("Plan complété !")
                setIsLoading(false)
                break

              case 'error':
                throw new Error(data.message)
            }
          }
        }
      }

    } catch (err) {
      console.error("Error creating orchestrated plan:", err)
      setError(err instanceof Error ? err.message : "Une erreur est survenue")
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleCreatePlan()
    }
  }

  const getNeedTypeLabel = (type: NeedType): string => {
    const labels: Record<NeedType, string> = {
      punctual_task: "Tâche ponctuelle",
      habit_skill: "Habitude/Compétence",
      complex_project: "Projet complexe",
      decision_research: "Décision/Recherche",
      social_event: "Événement social"
    }
    return labels[type] || type
  }
  const getAgentInfo = (agentType: AgentType) => {
    const agentConfig: Record<AgentType, { name: string; icon: any; color: string; description: string }> = {
      executive: {
        name: "Assistant Exécutif",
        icon: IconListCheck,
        color: "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400",
        description: "Organise et structure les tâches"
      },
      coach: {
        name: "Coach Personnel",
        icon: IconTrendingUp,
        color: "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400",
        description: "Guide votre progression"
      },
      strategist: {
        name: "Stratège",
        icon: IconTarget,
        color: "bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400",
        description: "Définit la vision globale"
      },
      planner: {
        name: "Planificateur",
        icon: IconCalendarEvent,
        color: "bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400",
        description: "Crée votre planning détaillé"
      },
      resource: {
        name: "Expert Ressources",
        icon: IconBulb,
        color: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400",
        description: "Identifie vos besoins"
      },
      research: {
        name: "Analyste",
        icon: IconSparkles,
        color: "bg-pink-100 dark:bg-pink-900/30 text-pink-600 dark:text-pink-400",
        description: "Compare et recommande"
      },
      social: {
        name: "Organisateur d'Événements",
        icon: IconCalendarEvent,
        color: "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400",
        description: "Coordonne vos événements"
      }
    }
    return agentConfig[agentType] || {
      name: "Assistant",
      icon: IconSparkles,
      color: "bg-gray-100 dark:bg-gray-900/30 text-gray-600 dark:text-gray-400",
      description: "Vous accompagne"
    }
  }

  const getComplexityColor = (complexity: string): string => {
    const colors: Record<string, string> = {
      simple: "bg-green-500",
      moderate: "bg-yellow-500",
      complex: "bg-orange-500",
      very_complex: "bg-red-500"
    }
    return colors[complexity] || "bg-gray-500"
  }

  const quickExamples = [
    "Je veux apprendre le piano en 6 mois",
    "Organiser un anniversaire pour 30 personnes",
    "Créer une application mobile",
    "Choisir la meilleure assurance auto",
    "Courir un semi-marathon d'ici 3 mois"
  ]

  return (
    <>
      <SiteHeader user={user} title="AI Planner" icon={Bot} />
      <div className="flex flex-1 flex-col h-[calc(100vh-4rem)]">
        <div className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
          
          {/* Input Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <IconSparkles className="size-5 text-purple-600" />
                Planificateur Intelligent Multi-Agents
              </CardTitle>
              <CardDescription>
                Décrivez votre objectif ou projet, et laissez notre système IA créer un plan structuré et actionnable
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Exemple : Je veux créer une startup dans l'intelligence artificielle..."
                  className="min-h-[120px] resize-none"
                  disabled={isLoading}
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Appuyez sur Ctrl+Enter ou Cmd+Enter pour générer le plan
                </p>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  onClick={handleCreatePlan}
                  disabled={!input.trim() || isLoading}
                  className="flex-1"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 size-4 animate-spin" />
                      Génération du plan...
                    </>
                  ) : (
                    <>
                      <IconSparkles className="mr-2 size-4" />
                      Générer un plan structuré
                    </>
                  )}
                </Button>
              </div>

              {/* Quick Examples */}
              {!plan && !isLoading && (
                <div className="space-y-2">
                  <p className="text-xs text-muted-foreground font-medium">
                    Exemples rapides :
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {quickExamples.map((example, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => setInput(example)}
                        className="text-xs"
                      >
                        {example}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="size-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Streaming Status */}
          {isLoading && (
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <Loader2 className="size-5 animate-spin text-purple-600" />
                  <div className="flex-1">
                    <p className="font-medium">{streamingStatus}</p>
                    {currentAgent && (
                      <p className="text-sm text-muted-foreground mt-1">
                        {getAgentInfo(currentAgent as AgentType).name} travaille sur votre demande...
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Classification progressive */}
          {classification && !plan && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">✓ Classification</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Type de besoin :</span>
                  <Badge variant="secondary" className="font-medium">
                    {getNeedTypeLabel(classification.need_type)}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Complexité :</span>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${getComplexityColor(classification.complexity)}`} />
                    <span className="text-sm font-medium capitalize">
                      {classification.complexity}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Agents progressifs */}
          {agentResponses.length > 0 && !plan && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Bot className="size-5" />
                  Experts Consultés ({agentResponses.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {agentResponses.map((agent, idx) => {
                    const agentInfo = getAgentInfo(agent.agent_type)
                    const Icon = agentInfo.icon
                    
                    return (
                      <div key={idx} className="border rounded-lg p-4 animate-in slide-in-from-left">
                        <div className="flex items-start gap-3">
                          <div className={`flex-shrink-0 w-10 h-10 rounded-full ${agentInfo.color} flex items-center justify-center`}>
                            <Icon className="size-5" />
                          </div>
                          <div className="flex-1 space-y-2">
                            <div className="flex items-center justify-between">
                              <div>
                                <h4 className="font-semibold">{agentInfo.name}</h4>
                                <p className="text-xs text-muted-foreground">{agentInfo.description}</p>
                              </div>
                              {agent.success ? (
                                <CheckCircle2 className="size-5 text-green-600 flex-shrink-0" />
                              ) : (
                                <AlertCircle className="size-5 text-red-600 flex-shrink-0" />
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground">{agent.message}</p>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Plan Results */}
          {plan && (
            <div className="space-y-4">
              {/* Classification Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Classification</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Type de besoin :</span>
                    <Badge variant="secondary" className="font-medium">
                      {getNeedTypeLabel(plan.classification.need_type)}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Complexité :</span>
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${getComplexityColor(plan.classification.complexity)}`} />
                      <span className="text-sm font-medium capitalize">
                        {plan.classification.complexity}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Confiance :</span>
                    <span className="text-sm font-medium">
                      {(plan.classification.confidence * 100).toFixed(0)}%
                    </span>
                  </div>

                  {plan.classification.key_characteristics.length > 0 && (
                    <div className="pt-2 border-t">
                      <p className="text-sm text-muted-foreground mb-2">Caractéristiques :</p>
                      <div className="flex flex-wrap gap-1">
                        {plan.classification.key_characteristics.map((char, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {char}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="pt-2 border-t">
                    <p className="text-sm text-muted-foreground">Raisonnement :</p>
                    <p className="text-sm mt-1">{plan.classification.reasoning}</p>
                  </div>
                </CardContent>
              </Card>              {/* Team Members Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Bot className="size-5" />
                    Votre Équipe d'Experts ({plan.agent_responses.length})
                  </CardTitle>
                  <CardDescription>
                    Plusieurs spécialistes ont collaboré pour créer votre plan personnalisé
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {plan.agent_responses.map((agent, idx) => {
                      const agentInfo = getAgentInfo(agent.agent_type)
                      const Icon = agentInfo.icon
                      
                      return (
                        <div key={idx} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex items-start gap-3">
                            <div className={`flex-shrink-0 w-10 h-10 rounded-full ${agentInfo.color} flex items-center justify-center`}>
                              <Icon className="size-5" />
                            </div>
                            <div className="flex-1 space-y-2">
                              <div className="flex items-center justify-between">
                                <div>
                                  <h4 className="font-semibold">{agentInfo.name}</h4>
                                  <p className="text-xs text-muted-foreground">{agentInfo.description}</p>
                                </div>
                                {agent.success ? (
                                  <CheckCircle2 className="size-5 text-green-600 flex-shrink-0" />
                                ) : (
                                  <AlertCircle className="size-5 text-red-600 flex-shrink-0" />
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground">{agent.message}</p>
                              
                              {agent.next_steps.length > 0 && (
                                <div className="mt-3 pt-3 border-t">
                                  <p className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                                    <IconListCheck className="size-3" />
                                    Recommandations :
                                  </p>
                                  <ul className="text-xs space-y-1.5">
                                    {agent.next_steps.slice(0, 3).map((step, stepIdx) => (
                                      <li key={stepIdx} className="flex items-start gap-2">
                                        <span className="text-purple-500 font-bold">→</span>
                                        <span className="flex-1">{step}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Summary Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Résumé du Plan</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <p className="whitespace-pre-wrap text-sm">{plan.summary}</p>
                  </div>
                </CardContent>
              </Card>

              {/* Created Resources */}
              {(plan.created_goals.length > 0 || plan.created_events.length > 0) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Ressources Créées</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {plan.created_goals.length > 0 && (
                        <Alert>
                          <IconTarget className="size-4" />
                          <AlertDescription>
                            <span className="font-medium">{plan.created_goals.length}</span> objectif(s) créé(s) dans votre liste d'objectifs.{" "}
                            <Button
                              variant="link"
                              size="sm"
                              onClick={() => router.push("/goals")}
                              className="p-0 h-auto"
                            >
                              Voir les objectifs →
                            </Button>
                          </AlertDescription>
                        </Alert>
                      )}
                      
                      {plan.created_events.length > 0 && (
                        <Alert>
                          <IconCalendarEvent className="size-4" />
                          <AlertDescription>
                            <span className="font-medium">{plan.created_events.length}</span> événement(s) créé(s) dans votre calendrier.{" "}
                            <Button
                              variant="link"
                              size="sm"
                              onClick={() => router.push("/calendar")}
                              className="p-0 h-auto"
                            >
                              Voir le calendrier →
                            </Button>
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2">
                <Button
                  onClick={() => {
                    setPlan(null)
                    setInput("")
                  }}
                  variant="outline"
                  className="flex-1"
                >
                  Nouveau plan
                </Button>
                {plan.created_goals.length > 0 && (
                  <Button
                    onClick={() => router.push("/goals")}
                    className="flex-1"
                  >
                    Voir mes objectifs
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
