"use client";

import { useState } from "react";
import { Suggestion } from "@/lib/api";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Clock, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";

interface SuggestionCardProps {
  suggestion: Suggestion;
  onAccept?: (id: string) => void;
  onReject?: (id: string) => void;
  className?: string;
}

const suggestionTypeConfig = {
  take_break: {
    emoji: "💆",
    color: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
    icon: Clock,
  },
  balance_day: {
    emoji: "⚖️",
    color: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
    icon: Lightbulb,
  },
  move_event: {
    emoji: "📅",
    color: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
    icon: Clock,
  },
};

const priorityConfig = {
  low: {
    color: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
    label: "Priorité basse",
  },
  medium: {
    color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
    label: "Priorité moyenne",
  },
  high: {
    color: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
    label: "Priorité haute",
  },
};

export function SuggestionCard({ suggestion, onAccept, onReject, className }: SuggestionCardProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  
  const typeConfig = suggestionTypeConfig[suggestion.type];
  const priorityStyle = priorityConfig[suggestion.priority];

  const handleAccept = async () => {
    if (onAccept) {
      setIsProcessing(true);
      try {
        await onAccept(suggestion.id);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const handleReject = async () => {
    if (onReject) {
      setIsProcessing(true);
      try {
        await onReject(suggestion.id);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <Card className={cn("transition-all hover:shadow-md", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 flex-1">
            <span className="text-2xl">{typeConfig.emoji}</span>
            <CardTitle className="text-lg leading-tight">{suggestion.title}</CardTitle>
          </div>
          <Badge className={priorityStyle.color} variant="secondary">
            {priorityStyle.label}
          </Badge>
        </div>
        <CardDescription className="text-xs text-muted-foreground">
          Suggéré {formatDate(suggestion.created_at)}
        </CardDescription>
      </CardHeader>

      <CardContent className="pb-4">
        <p className="text-sm text-muted-foreground leading-relaxed">
          {suggestion.description}
        </p>
        
        {suggestion.extra_data && (
          <div className="mt-3 p-2 bg-muted/50 rounded-md">
            <details className="text-xs">
              <summary className="cursor-pointer text-muted-foreground hover:text-foreground transition-colors">
                Détails supplémentaires
              </summary>
              <pre className="mt-2 text-xs overflow-x-auto">
                {JSON.stringify(JSON.parse(suggestion.extra_data), null, 2)}
              </pre>
            </details>
          </div>
        )}
      </CardContent>

      {suggestion.status === 'pending' && (
        <CardFooter className="flex gap-2 pt-0">
          <Button
            onClick={handleAccept}
            disabled={isProcessing}
            size="sm"
            className="flex-1"
            variant="default"
          >
            <CheckCircle2 className="h-4 w-4 mr-1" />
            Accepter
          </Button>
          <Button
            onClick={handleReject}
            disabled={isProcessing}
            size="sm"
            className="flex-1"
            variant="outline"
          >
            <XCircle className="h-4 w-4 mr-1" />
            Ignorer
          </Button>
        </CardFooter>
      )}

      {suggestion.status === 'accepted' && (
        <CardFooter className="pt-0">
          <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
            <CheckCircle2 className="h-4 w-4" />
            <span>Suggestion acceptée</span>
          </div>
        </CardFooter>
      )}

      {suggestion.status === 'rejected' && (
        <CardFooter className="pt-0">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <XCircle className="h-4 w-4" />
            <span>Suggestion ignorée</span>
          </div>
        </CardFooter>
      )}
    </Card>
  );
}

