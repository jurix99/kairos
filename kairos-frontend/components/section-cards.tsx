import { IconTrendingDown, IconTrendingUp, IconCalendar, IconCircleCheck, IconClock, IconAlertCircle } from "@tabler/icons-react"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { Event, Category } from "@/lib/api"

interface SectionCardsProps {
  events: Event[]
  categories: Category[]
}

export function SectionCards({ events, categories }: SectionCardsProps) {
  // Calculate statistics
  const totalEvents = events.length
  const completedEvents = events.filter(e => e.status === 'completed').length
  const pendingEvents = events.filter(e => e.status === 'pending').length
  const inProgressEvents = events.filter(e => e.status === 'in-progress').length
  const highPriorityEvents = events.filter(e => e.priority === 'high').length

  // Calculate completion rate
  const completionRate = totalEvents > 0 
    ? Math.round((completedEvents / totalEvents) * 100) 
    : 0

  // Calculate events this week
  const now = new Date()
  const weekStart = new Date(now.setDate(now.getDate() - now.getDay()))
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekEnd.getDate() + 7)
  
  const eventsThisWeek = events.filter(event => {
    const eventDate = new Date(event.start_time)
    return eventDate >= weekStart && eventDate <= weekEnd
  }).length

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-4 lg:px-6">
      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Total Events</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl flex items-center gap-2">
            <IconCalendar className="size-6 text-purple-500" />
            {totalEvents}
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              <IconTrendingUp />
              {eventsThisWeek} this week
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {categories.length} categories
          </div>
          <div className="text-muted-foreground">
            All your scheduled events
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Completed</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl flex items-center gap-2">
            <IconCircleCheck className="size-6 text-green-500" />
            {completedEvents}
          </CardTitle>
          <CardAction>
            <Badge variant="outline" className="text-green-600">
              <IconTrendingUp />
              {completionRate}%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {completionRate}% completion rate <IconTrendingUp className="size-4" />
          </div>
          <div className="text-muted-foreground">
            Successfully finished tasks
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>In Progress</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl flex items-center gap-2">
            <IconClock className="size-6 text-blue-500" />
            {inProgressEvents}
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              {pendingEvents} pending
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            Active tasks ongoing
          </div>
          <div className="text-muted-foreground">
            {pendingEvents} waiting to start
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>High Priority</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl flex items-center gap-2">
            <IconAlertCircle className="size-6 text-red-500" />
            {highPriorityEvents}
          </CardTitle>
          <CardAction>
            <Badge variant="outline" className={highPriorityEvents > 0 ? "text-red-600" : ""}>
              {highPriorityEvents > 0 ? (
                <><IconAlertCircle /> Needs attention</>
              ) : (
                <><IconCircleCheck /> All clear</>
              )}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {highPriorityEvents > 0 ? 'Urgent tasks require focus' : 'No urgent tasks'}
          </div>
          <div className="text-muted-foreground">
            Priority management
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
