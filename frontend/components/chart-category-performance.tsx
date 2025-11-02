"use client"

import { useMemo } from "react"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import type { Event, Category } from "@/lib/api"

const chartConfig = {
  completed: {
    label: "Completed",
    color: "hsl(142, 76%, 36%)",
  },
  pending: {
    label: "Pending/In Progress",
    color: "hsl(221, 83%, 53%)",
  },
} satisfies ChartConfig

interface ChartCategoryPerformanceProps {
  events: Event[]
  categories: Category[]
}

export function ChartCategoryPerformance({ events, categories }: ChartCategoryPerformanceProps) {
  const categoryStats = useMemo(() => {
    const stats = categories.map((category) => {
      const categoryEvents = events.filter(
        (event) => event.category.id === category.id
      )
      
      const completed = categoryEvents.filter(
        (e) => e.status === "completed"
      ).length
      
      const pending = categoryEvents.filter(
        (e) => e.status === "pending" || e.status === "in-progress"
      ).length

      return {
        categoryName: category.name.length > 15 
          ? category.name.substring(0, 15) + '...' 
          : category.name,
        completed,
        pending,
        total: categoryEvents.length,
      }
    })

    // Only show categories with events
    return stats.filter((stat) => stat.total > 0)
  }, [events, categories])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Category Performance</CardTitle>
        <CardDescription>
          Completed vs Pending events by category
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <BarChart data={categoryStats}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="categoryName"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar 
              dataKey="completed" 
              fill="var(--color-completed)" 
              radius={[4, 4, 0, 0]} 
            />
            <Bar 
              dataKey="pending" 
              fill="var(--color-pending)" 
              radius={[4, 4, 0, 0]} 
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

