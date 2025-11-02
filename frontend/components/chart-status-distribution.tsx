"use client"

import { useMemo } from "react"
import { Cell, Pie, PieChart } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import type { Event } from "@/lib/api"

const chartConfig = {
  completed: {
    label: "Completed",
    color: "hsl(142, 76%, 36%)",
  },
  "in-progress": {
    label: "In Progress",
    color: "hsl(221, 83%, 53%)",
  },
  pending: {
    label: "Pending",
    color: "hsl(38, 92%, 50%)",
  },
  cancelled: {
    label: "Cancelled",
    color: "hsl(0, 72%, 51%)",
  },
} satisfies ChartConfig

interface ChartStatusDistributionProps {
  events: Event[]
}

export function ChartStatusDistribution({ events }: ChartStatusDistributionProps) {
  const statusData = useMemo(() => {
    const counts = {
      completed: 0,
      "in-progress": 0,
      pending: 0,
      cancelled: 0,
    }

    events.forEach((event) => {
      if (event.status in counts) {
        counts[event.status as keyof typeof counts]++
      }
    })

    return Object.entries(counts)
      .filter(([_, value]) => value > 0) // Only show statuses with events
      .map(([name, value]) => ({
        name,
        value,
        fill: chartConfig[name as keyof typeof chartConfig]?.color || "hsl(0, 0%, 50%)",
      }))
  }, [events])

  const total = useMemo(() => {
    return statusData.reduce((acc, item) => acc + item.value, 0)
  }, [statusData])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Status Distribution</CardTitle>
        <CardDescription>
          Overview of event statuses
        </CardDescription>
      </CardHeader>
      <CardContent className="flex items-center justify-center pb-0">
        <ChartContainer config={chartConfig} className="mx-auto aspect-square h-[300px]">
          <PieChart>
            <ChartTooltip 
              content={<ChartTooltipContent nameKey="name" hideLabel />} 
            />
            <Pie 
              data={statusData} 
              dataKey="value" 
              nameKey="name"
              innerRadius={60}
              strokeWidth={5}
            >
              {statusData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

