"use client"

import { Loader2 } from "lucide-react"
import { memo } from "react"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useChatModels } from "@/hooks/use-models"
import type { ModelSelectorProps } from "@/types"

function ModelSelectorComponent({
  selectedModel,
  onModelChange,
  disabled = false,
}: ModelSelectorProps) {
  const { chatModels, defaultModel, isLoading, error } = useChatModels()

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm text-muted-foreground">Loading models...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2">
        <span className="text-sm text-destructive">{error}</span>
      </div>
    )
  }

  return (
    <Select value={selectedModel || defaultModel} onValueChange={onModelChange} disabled={disabled}>
      <SelectTrigger className="w-[200px] h-8 text-sm">
        <SelectValue placeholder="Select model" />
      </SelectTrigger>
      <SelectContent>
        {chatModels.map(model => (
          <SelectItem key={model.id} value={model.id} className="text-sm">
            <div className="flex items-center justify-between w-full">
              <span className="font-medium">{model.id}</span>
              <span className="text-xs text-muted-foreground ml-2">{model.owned_by}</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

export const ModelSelector = memo(ModelSelectorComponent)
