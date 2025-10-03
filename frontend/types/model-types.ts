export interface ModelInfo {
  id: string
  object: string
  created: number
  owned_by: string
}

export interface ModelsResponse {
  models: ModelInfo[]
  default_model: string
}

export interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (modelId: string) => void
  disabled?: boolean
}
