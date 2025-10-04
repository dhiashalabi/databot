export interface TypingOptions {
  wordDelay?: number
  randomDelay?: number
  onWordTyped?: (text: string) => void
  onTypingStart?: () => void
  onTypingComplete?: () => void
}

export async function typeText(text: string, options: TypingOptions = {}): Promise<void> {
  const { wordDelay = 2, randomDelay = 1, onWordTyped, onTypingStart, onTypingComplete } = options

  const words = text.split(" ")
  let currentText = ""

  onTypingStart?.()

  for (let i = 0; i < words.length; i++) {
    currentText += words[i] + (i < words.length - 1 ? " " : "")

    onWordTyped?.(currentText)

    const delay = wordDelay + Math.random() * randomDelay
    await new Promise(resolve => setTimeout(resolve, delay))
  }

  onTypingComplete?.()
}

export async function typeTextWithUpdate(
  text: string,
  updateFn: (text: string) => void,
  options: TypingOptions = {}
): Promise<void> {
  return typeText(text, {
    ...options,
    onWordTyped: updateFn,
  })
}

export async function typeTextDebounced(
  text: string,
  updateFn: (text: string) => void,
  debounceMs: number = 50,
  options: TypingOptions = {}
): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, debounceMs))

  return typeTextWithUpdate(text, updateFn, options)
}
