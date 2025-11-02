"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { SiteHeader } from "@/components/site-header"
import { useAuth } from "@/contexts/auth-context"
import { IconRobot, IconSend, IconUser, IconSparkles, IconCalendarPlus } from "@tabler/icons-react"
import { Bot } from "lucide-react"
import { apiClient, ExtractedEvent, ChatResponse } from "@/lib/api"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  events?: ExtractedEvent[]
  action?: string
}

export default function AssistantPage() {
  const { user } = useAuth()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your AI assistant for Kairos. I can help you manage your schedule, analyze your productivity, and suggest optimizations for your calendar. How can I help you today?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [pendingEvents, setPendingEvents] = useState<ExtractedEvent[]>([])
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      // Préparer l'historique de conversation
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Appeler l'API assistant
      const response: ChatResponse = await apiClient.chatWithAssistant({
        message: userMessage.content,
        conversation_history: conversationHistory
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.message,
        timestamp: new Date(),
        events: response.events,
        action: response.action
      }

      setMessages((prev) => [...prev, assistantMessage])

      // Si des événements ont été extraits, les stocker pour confirmation
      if (response.action === "create_events" && response.events.length > 0) {
        setPendingEvents(response.events)
      }

    } catch (error) {
      console.error("Error chatting with assistant:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Désolé, j'ai rencontré une erreur lors du traitement de votre message. Veuillez réessayer.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateEvents = async () => {
    if (pendingEvents.length === 0) return

    setIsLoading(true)
    try {
      const response = await apiClient.createEventsFromAssistant({
        events: pendingEvents
      })

      const confirmationMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: response.message,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, confirmationMessage])
      setPendingEvents([])

    } catch (error) {
      console.error("Error creating events:", error)
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: "Désolé, j'ai rencontré une erreur lors de la création des événements.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleRejectEvents = () => {
    setPendingEvents([])
    const rejectionMessage: Message = {
      id: Date.now().toString(),
      role: "assistant",
      content: "D'accord, je n'ai pas créé ces événements. Y a-t-il autre chose que je puisse faire pour vous ?",
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, rejectionMessage])
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const quickActions = [
    "Show my schedule for today",
    "What's my most productive time?",
    "Analyze my calendar patterns",
    "Add a meeting with John tomorrow at 2pm",
  ]

  return (
    <>
      <SiteHeader user={user} title="AI Assistant" icon={Bot} />
      <div className="flex flex-1 flex-col h-[calc(100vh-4rem)]">
        <div className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">     
          {/* Chat Container */}
          <Card className="flex-1 flex flex-col overflow-hidden">
            <CardHeader className="pb-3">
              <CardTitle>Conversation</CardTitle>
              <CardDescription>
                Ask me anything about your schedule and productivity
              </CardDescription>
            </CardHeader>
            <Separator />
            
            {/* Messages Area */}
            <CardContent className="flex-1 flex flex-col p-0">
              <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${
                        message.role === "user" ? "flex-row-reverse" : "flex-row"
                      }`}
                    >
                      {/* Avatar */}
                      <div
                        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                          message.role === "user"
                            ? "bg-primary"
                            : "bg-gradient-to-br from-purple-600 to-pink-600"
                        }`}
                      >
                        {message.role === "user" ? (
                          <IconUser className="size-4 text-primary-foreground" />
                        ) : (
                          <IconRobot className="size-4 text-white" />
                        )}
                      </div>

                      {/* Message Content */}
                      <div
                        className={`flex flex-col gap-1 ${
                          message.role === "user" ? "items-end" : "items-start"
                        } max-w-[80%]`}
                      >
                        <div
                          className={`rounded-lg px-4 py-2 ${
                            message.role === "user"
                              ? "bg-primary text-primary-foreground"
                              : "bg-muted"
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">
                            {message.content}
                          </p>
                          
                          {/* Afficher les événements extraits */}
                          {message.events && message.events.length > 0 && (
                            <div className="mt-3 space-y-2">
                              <p className="text-xs font-medium opacity-80">Événements détectés :</p>
                              {message.events.map((event, idx) => (
                                <div key={idx} className="bg-background/50 rounded p-2 text-xs">
                                  <div className="font-medium">{event.title}</div>
                                  <div className="opacity-70">
                                    {new Date(event.start_time).toLocaleString('fr-FR')} - {new Date(event.end_time).toLocaleString('fr-FR')}
                                  </div>
                                  {event.location && <div className="opacity-70">📍 {event.location}</div>}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground px-2">
                          {message.timestamp.toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                    </div>
                  ))}

                  {/* Loading indicator */}
                  {isLoading && (
                    <div className="flex gap-3">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-purple-600 to-pink-600">
                        <IconRobot className="size-4 text-white" />
                      </div>
                      <div className="flex items-center gap-1 rounded-lg bg-muted px-4 py-2">
                        <div className="flex gap-1">
                          <div className="h-2 w-2 animate-bounce rounded-full bg-foreground/60 [animation-delay:-0.3s]"></div>
                          <div className="h-2 w-2 animate-bounce rounded-full bg-foreground/60 [animation-delay:-0.15s]"></div>
                          <div className="h-2 w-2 animate-bounce rounded-full bg-foreground/60"></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              <Separator />

              {/* Quick Actions */}
              {messages.length <= 1 && (
                <div className="p-4 space-y-2">
                  <p className="text-xs text-muted-foreground font-medium">
                    Quick actions:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {quickActions.map((action, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setInput(action)
                          setTimeout(() => handleSendMessage(), 100)
                        }}
                        className="text-xs"
                      >
                        {action}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* Confirmation des événements en attente */}
              {pendingEvents.length > 0 && (
                <>
                  <Separator />
                  <div className="p-4 bg-blue-50 dark:bg-blue-950/20">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium flex items-center gap-2">
                        <IconCalendarPlus className="size-4" />
                        Créer ces événements ?
                      </h4>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        onClick={handleCreateEvents}
                        disabled={isLoading}
                        size="sm"
                        className="flex-1"
                      >
                        Oui, créer les événements
                      </Button>
                      <Button 
                        onClick={handleRejectEvents}
                        disabled={isLoading}
                        variant="outline"
                        size="sm"
                        className="flex-1"
                      >
                        Non, annuler
                      </Button>
                    </div>
                  </div>
                </>
              )}

              <Separator />

              {/* Input Area */}
              <div className="p-4">
                <div className="flex gap-2">
                  <Textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
                    className="min-h-[60px] max-h-[200px] resize-none"
                    disabled={isLoading}
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!input.trim() || isLoading}
                    size="icon"
                    className="h-[60px] w-[60px] shrink-0"
                  >
                    <IconSend className="size-5" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Press Enter to send • Shift+Enter for new line
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}
