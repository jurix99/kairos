"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Progress } from "@/components/ui/progress"
import type { Event, Category } from "@/lib/api"

interface CategoryStatsTableProps {
  events: Event[]
  categories: Category[]
}

export function CategoryStatsTable({ events, categories }: CategoryStatsTableProps) {
  const categoryStats = useMemo(() => {
    return categories.map((category) => {
      const categoryEvents = events.filter(
        (event) => event.category.id === category.id
      )
      
      const total = categoryEvents.length
      const completed = categoryEvents.filter((e) => e.status === "completed").length
      const pending = categoryEvents.filter(
        (e) => e.status === "pending" || e.status === "in-progress"
      ).length
      const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0

      return {
        id: category.id,
        name: category.name,
        color: category.color_code,
        total,
        completed,
        pending,
        completionRate,
      }
    })
    .filter((stat) => stat.total > 0) // Only show categories with events
    .sort((a, b) => b.total - a.total) // Sort by total events
  }, [events, categories])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Category Statistics</CardTitle>
        <CardDescription>
          Detailed breakdown of events by category
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Category</TableHead>
              <TableHead className="text-right">Total</TableHead>
              <TableHead className="text-right">Completed</TableHead>
              <TableHead className="text-right">Pending</TableHead>
              <TableHead>Completion Rate</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {categoryStats.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  No events found
                </TableCell>
              </TableRow>
            ) : (
              categoryStats.map((stat) => (
                <TableRow key={stat.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: stat.color }}
                      />
                      <span className="font-medium">{stat.name}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    {stat.total}
                  </TableCell>
                  <TableCell className="text-right text-green-600 dark:text-green-400">
                    {stat.completed}
                  </TableCell>
                  <TableCell className="text-right text-blue-600 dark:text-blue-400">
                    {stat.pending}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Progress value={stat.completionRate} className="flex-1" />
                      <span className="text-sm text-muted-foreground min-w-[3rem] text-right">
                        {stat.completionRate}%
                      </span>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

