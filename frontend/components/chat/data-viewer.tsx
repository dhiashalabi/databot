"use client"

import { ChevronDown } from "lucide-react"

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface DataViewerProps {
  data: unknown
}

export function DataViewer({ data }: DataViewerProps) {
  const dataArray = Array.isArray(data) ? data : [data]

  const flattenObject = (obj: Record<string, unknown>, prefix = ""): Record<string, unknown> => {
    return Object.keys(obj).reduce(
      (acc, key) => {
        const value = obj[key]
        const newKey = prefix ? `${prefix}.${key}` : key

        if (value && typeof value === "object" && !Array.isArray(value)) {
          Object.assign(acc, flattenObject(value as Record<string, unknown>, newKey))
        } else {
          acc[newKey] = value
        }

        return acc
      },
      {} as Record<string, unknown>
    )
  }

  const getAllKeys = () => {
    const allKeys = new Set<string>()
    dataArray.forEach(item => {
      if (item && typeof item === "object") {
        const flattened = flattenObject(item as Record<string, unknown>)
        Object.keys(flattened).forEach(key => allKeys.add(key))
      }
    })
    return Array.from(allKeys)
  }

  const keys = getAllKeys()

  const formatValue = (value: unknown): string => {
    if (value === null || value === undefined) return "-"
    if (typeof value === "boolean") return value ? "Yes" : "No"
    if (typeof value === "number") {
      return value.toLocaleString(undefined, {
        maximumFractionDigits: 2,
      })
    }
    if (typeof value === "object") return JSON.stringify(value)
    return String(value)
  }

  return (
    <Collapsible className="w-full">
      <CollapsibleTrigger className="flex w-full items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-left text-sm text-card-foreground transition-colors hover:bg-accent hover:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground">
        <ChevronDown className="h-4 w-4 transition-transform duration-200 data-[state=closed]:rotate-[-90deg]" />
        <span>📊 View data details</span>
      </CollapsibleTrigger>

      <CollapsibleContent className="mt-2">
        <Tabs defaultValue="table" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-muted">
            <TabsTrigger
              value="table"
              className="data-[state=active]:bg-background data-[state=active]:text-foreground"
            >
              Table
            </TabsTrigger>
            <TabsTrigger
              value="raw"
              className="data-[state=active]:bg-background data-[state=active]:text-foreground"
            >
              Raw Data
            </TabsTrigger>
          </TabsList>

          <TabsContent value="table" className="mt-4">
            <ScrollArea className="h-96 w-2xl rounded-lg border border-border">
              <div className="min-w-max">
                <Table>
                  <TableHeader className="sticky top-0 z-10 bg-muted">
                    <TableRow className="border-border hover:bg-muted/50">
                      <TableHead className="sticky left-0 z-20 w-48 bg-muted text-muted-foreground">
                        Field
                      </TableHead>
                      {dataArray.map((_, index) => (
                        <TableHead key={index} className="w-40 text-muted-foreground">
                          {dataArray.length > 1 ? `Record ${index + 1}` : "Value"}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {keys.map(key => (
                      <TableRow key={key} className="border-border hover:bg-muted/50">
                        <TableCell className="sticky left-0 z-10 w-48 bg-muted font-medium text-foreground">
                          {key}
                        </TableCell>
                        {dataArray.map((item, index) => {
                          const flattened = flattenObject(item as Record<string, unknown>)
                          return (
                            <TableCell key={index} className="w-40 text-muted-foreground">
                              {formatValue(flattened[key])}
                            </TableCell>
                          )
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              <ScrollBar orientation="horizontal" />
              <ScrollBar orientation="vertical" />
            </ScrollArea>
          </TabsContent>

          <TabsContent value="raw" className="mt-4">
            <pre className="overflow-x-auto rounded-lg bg-muted p-4 text-xs text-muted-foreground">
              {JSON.stringify(data, null, 2)}
            </pre>
          </TabsContent>
        </Tabs>
      </CollapsibleContent>
    </Collapsible>
  )
}
