"use client";

import { useEffect, useState } from "react";
import { apiClient, Suggestion } from "@/lib/api";
import { SuggestionCard } from "./suggestion-card";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Sparkles, RefreshCw, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export function SuggestionsPanel() {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const { toast } = useToast();

  const loadSuggestions = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getSuggestions('pending');
      setSuggestions(data);
    } catch (error) {
      console.error('Error loading suggestions:', error);
      toast({
        title: "Erreur",
        description: "Impossible de charger les suggestions",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const generateSuggestions = async () => {
    try {
      setIsGenerating(true);
      const newSuggestions = await apiClient.generateSuggestions();
      
      if (newSuggestions.length === 0) {
        toast({
          title: "Aucune nouvelle suggestion",
          description: "Aucune nouvelle suggestion n'a été générée pour le moment",
        });
      } else {
        toast({
          title: "Suggestions générées",
          description: `${newSuggestions.length} nouvelle(s) suggestion(s) générée(s)`,
        });
        await loadSuggestions();
      }
    } catch (error) {
      console.error('Error generating suggestions:', error);
      toast({
        title: "Erreur",
        description: "Impossible de générer des suggestions",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAccept = async (id: string) => {
    try {
      await apiClient.updateSuggestion(id, { status: 'accepted' });
      toast({
        title: "Suggestion acceptée",
        description: "La suggestion a été marquée comme acceptée",
      });
      await loadSuggestions();
    } catch (error) {
      console.error('Error accepting suggestion:', error);
      toast({
        title: "Erreur",
        description: "Impossible d'accepter la suggestion",
        variant: "destructive",
      });
    }
  };

  const handleReject = async (id: string) => {
    try {
      await apiClient.updateSuggestion(id, { status: 'rejected' });
      toast({
        title: "Suggestion ignorée",
        description: "La suggestion a été ignorée",
      });
      await loadSuggestions();
    } catch (error) {
      console.error('Error rejecting suggestion:', error);
      toast({
        title: "Erreur",
        description: "Impossible d'ignorer la suggestion",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    loadSuggestions();
  }, []);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Suggestions de Kairos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Suggestions de Kairos
            </CardTitle>
            <CardDescription className="mt-1">
              {suggestions.length === 0 
                ? "Aucune suggestion active" 
                : `${suggestions.length} suggestion(s) active(s)`
              }
            </CardDescription>
          </div>
          <Button
            onClick={generateSuggestions}
            disabled={isGenerating}
            size="sm"
            variant="outline"
          >
            {isGenerating ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-1" />
            )}
            Générer
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        {suggestions.length === 0 ? (
          <div className="text-center py-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
              <Sparkles className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              Aucune suggestion active pour le moment
            </p>
            <Button onClick={generateSuggestions} disabled={isGenerating} size="sm">
              Générer des suggestions
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {suggestions.map((suggestion) => (
              <SuggestionCard
                key={suggestion.id}
                suggestion={suggestion}
                onAccept={handleAccept}
                onReject={handleReject}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

