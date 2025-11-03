"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";

export function useSuggestionsCount() {
  const [count, setCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadCount = async () => {
      try {
        const suggestions = await apiClient.getSuggestions('pending');
        setCount(suggestions.length);
      } catch (error) {
        console.error('Error loading suggestions count:', error);
        setCount(0);
      } finally {
        setIsLoading(false);
      }
    };

    loadCount();

    // Refresh count every 2 minutes
    const interval = setInterval(loadCount, 2 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  return { count, isLoading };
}

