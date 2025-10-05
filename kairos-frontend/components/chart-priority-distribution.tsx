"use client"

import { useMemo } from "react"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import type { Event } from "@/lib/api"

const chartConfig = {
  count: {
    label: "Events",
  },
  high: {
    label: "High",
    color: "hsl(0, 72%, 51%)",
  },
  medium: {
    label: "Medium",
    color: "hsl(38, 92%, 50%)",
  },
  low: {
    label: "Low",
    color: "hsl(142, 76%, 36%)",
  },
} satisfies ChartConfig

interface ChartPriorityDistributionProps {
  events: Event[]
}

export function ChartPriorityDistribution({ events }: ChartPriorityDistributionProps) {
  const priorityData = useMemo(() => {
    const counts = {
      high: 0,
      medium: 0,
      low: 0,
    }

    events.forEach((event) => {
      if (event.priority in counts) {
        counts[event.priority as keyof typeof counts]++
      }
    })

    return Object.entries(counts).map(([priority, count]) => ({
      priority: priority.charAt(0).toUpperCase() + priority.slice(1),
      count,
      fill: chartConfig[priority as keyof typeof chartConfig]?.color || "hsl(0, 0%, 50%)",
    }))
  }, [events])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Priority Distribution</CardTitle>
        <CardDescription>
          Events grouped by priority level
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <BarChart data={priorityData}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="priority"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
            />
            <YAxis />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar 
              dataKey="count" 
              radius={[8, 8, 0, 0]} 
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

