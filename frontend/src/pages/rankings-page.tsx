import { useState, useEffect, useMemo, useCallback } from "react"
import { motion } from "framer-motion"
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  createColumnHelper,
  flexRender,
  type SortingState,
  type ColumnFiltersState,
} from "@tanstack/react-table"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MetricCardSkeleton, ChartSkeleton } from "@/components/ui/skeleton"
import { cn, formatScore } from "@/lib/utils"
import { getRankings } from "@/lib/api"
import { PageHeader } from "@/components/layout/page-header"
import type { RankingEntry } from "@/types"
import {
  Search,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Trophy,
  Star,
  Filter,
  Download,
  AlertTriangle,
  Loader2,
} from "lucide-react"

const columnHelper = createColumnHelper<RankingEntry>()

const columns = [
  columnHelper.accessor("rank", {
    header: "Rank",
    cell: (info) => {
      const rank = info.getValue()
      let medal = ""
      if (rank === 1) medal = "🥇"
      else if (rank === 2) medal = "🥈"
      else if (rank === 3) medal = "🥉"
      return (
        <div className="flex items-center gap-1.5 font-mono text-sm font-semibold">
          {medal && <span className="text-base">{medal}</span>}
          <span className={rank <= 3 ? "text-brand-600" : "text-text-muted"}>
            #{rank}
          </span>
        </div>
      )
    },
    enableSorting: true,
  }),
  columnHelper.accessor("candidateId", {
    header: "Candidate",
    cell: (info) => {
      const row = info.row.original
      return (
        <div className="min-w-0">
          <span className="font-mono text-sm text-text-primary block">
            {info.getValue()}
          </span>
          {row.title && (
            <span className="text-[11px] text-text-muted block truncate">
              {row.title}{row.company ? ` at ${row.company}` : ""}
            </span>
          )}
        </div>
      )
    },
    enableSorting: true,
  }),
  columnHelper.accessor("score", {
    header: "Score",
    cell: (info) => (
      <span className="font-mono text-sm font-semibold text-text-primary">
        {formatScore(info.getValue())}
      </span>
    ),
    enableSorting: true,
  }),
  columnHelper.accessor("badge", {
    header: "Status",
    cell: (info) => <Badge variant={info.getValue()} />,
    enableSorting: true,
    filterFn: "equals",
  }),
  columnHelper.accessor("reasoning", {
    header: "AI Reasoning",
    cell: (info) => (
      <span className="text-xs text-text-muted line-clamp-2 max-w-[400px]">
        {info.getValue()}
      </span>
    ),
    enableSorting: false,
  }),
  columnHelper.display({
    id: "actions",
    cell: () => (
      <div className="flex gap-1">
        <Button variant="ghost" size="sm" className="h-7 px-2 text-xs">
          <Star className="w-3 h-3 mr-1" />
          Save
        </Button>
      </div>
    ),
  }),
]

export function RankingsPage() {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState("")
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set())
  const [data, setData] = useState<RankingEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let ignore = false
    getRankings()
      .then((result) => {
        if (!ignore) {
          setData(result.rankings)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!ignore) {
          console.error("Failed to load rankings:", err)
          setError("Could not connect to the ranking backend. Make sure the API server is running on port 8000.")
          setLoading(false)
        }
      })
    return () => { ignore = true }
  }, [])

  const toggleCard = useCallback((idx: number) => {
    setExpandedCards((prev) => {
      const next = new Set(prev)
      if (next.has(idx)) next.delete(idx)
      else next.add(idx)
      return next
    })
  }, [])

  const handleExport = useCallback(() => {
    if (data.length === 0) return
    const csv = [
      "rank,candidate_id,score,badge,reasoning",
      ...data.map(r =>
        `${r.rank},"${r.candidateId}",${r.score},"${r.badge}","${(r.reasoning || "").replace(/"/g, '""')}"`
      )
    ].join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "rankings_export.csv"
    a.click()
    URL.revokeObjectURL(url)
  }, [data])

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: { pageSize: 15 },
    },
  })

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-[12px] border border-danger/20 bg-danger/5 p-4 flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 text-danger shrink-0" />
          <div>
            <p className="text-sm font-medium text-danger">Connection Error</p>
            <p className="text-xs text-text-muted mt-0.5">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
        <div className="flex items-center gap-3">
          <Loader2 className="w-5 h-5 animate-spin text-brand-500" />
          <p className="text-sm text-text-muted">Running ranking pipeline on candidate data...</p>
        </div>
        <div className="grid-metrics gap-3">
          {Array.from({ length: 3 }).map((_, i) => <MetricCardSkeleton key={i} />)}
        </div>
        <ChartSkeleton />
      </div>
    )
  }

  return (
    <div className="relative space-y-6 max-w-[2200px] mx-auto min-h-[calc(100vh-3.5rem)] px-[clamp(1rem,3vw,3rem)] py-[clamp(1rem,3vw,2rem)]">
      {/* Background glow */}
      <div className="absolute top-20 right-1/4 w-1/3 h-64 bg-brand-500/5 blur-[120px] rounded-full pointer-events-none -z-10" />
      
      <PageHeader
        title="Candidate Rankings"
        description={`AI-powered ranking of ${data.length} candidates`}
        actions={
          <>
            <Button variant="outline" size="sm" className="h-8">
              <Filter className="w-3.5 h-3.5 mr-1.5" />
              Filters
            </Button>
            <Button variant="gradient" size="sm" className="h-8" onClick={handleExport}>
              <Download className="w-3.5 h-3.5 mr-1.5" />
              Export
            </Button>
          </>
        }
      />

      {/* Top 3 Highlight */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="grid-auto-responsive gap-3"
      >
        {data.slice(0, 3).map((c, i) => (
          <div key={c.candidateId} className="group relative rounded-xl border border-border-light bg-surface/40 backdrop-blur-md p-4 shadow-sm hover:shadow-premium transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-xl" />
            
            <div className="relative flex items-center gap-4">
              <div className={cn(
                "w-12 h-12 rounded-[10px] flex items-center justify-center text-xl font-bold border border-border-light shadow-inner-button",
                i === 0 ? "bg-amber-500/10 text-amber-500 border-amber-500/20" :
                i === 1 ? "bg-slate-300/10 text-slate-300 border-slate-300/20" :
                "bg-orange-500/10 text-orange-500 border-orange-500/20"
              )}>
                  {["🥇", "🥈", "🥉"][i]}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-semibold text-text-primary">
                      {c.candidateId}
                    </span>
                    <Badge variant={c.badge} />
                  </div>
                  <p className="text-[12px] text-text-muted truncate mt-1">
                    {c.title ? `${c.title}${c.company ? ` at ${c.company}` : ""}` : c.reasoning}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-mono text-xl font-semibold text-brand-400">
                    {formatScore(c.score)}
                  </p>
                  <p className="text-[10px] text-text-dim uppercase tracking-[0.05em] mt-0.5">
                    Match Score
                  </p>
                </div>
              </div>
          </div>
        ))}
      </motion.div>

      {/* Search + Filter Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 bg-surface/50 p-2 rounded-xl border border-border-light backdrop-blur-md shadow-sm">
        <div className="relative flex-1 w-full max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-dim" />
          <input
            type="text"
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Search candidates..."
            className="w-full h-9 pl-9 pr-3 bg-transparent text-[13px] text-text-primary placeholder:text-text-dim focus:outline-none transition-all"
          />
        </div>
        <div className="w-px h-5 bg-border-light hidden sm:block mx-1" />
        <select className="h-9 px-3 bg-transparent text-[13px] text-text-secondary focus:outline-none cursor-pointer hover:text-text-primary transition-colors">
          <option>All Statuses</option>
          <option>Verified</option>
          <option>Suspicious</option>
          <option>Honeypot</option>
        </select>
      </div>

      {/* Table — desktop table, mobile card mode */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.2 }}
        className="rounded-xl border border-border-light bg-surface/40 backdrop-blur-md overflow-hidden shadow-premium"
      >
        <div className="hidden sm:block overflow-x-auto">
          <table className="w-full">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id} className="border-b border-border-light bg-surface-secondary/50">
                      {headerGroup.headers.map((header) => (
                        <th
                          key={header.id}
                          className={cn(
                            "px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-text-muted cursor-pointer select-none hover:text-text-primary transition-colors",
                            header.column.getCanSort() && "cursor-pointer"
                          )}
                          onClick={header.column.getToggleSortingHandler()}
                        >
                          <div className="flex items-center gap-1">
                            {flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                            {header.column.getCanSort() && (
                              <ArrowUpDown className="w-3 h-3" />
                            )}
                          </div>
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>
                <tbody>
                  {table.getRowModel().rows.map((row, idx) => (
                    <motion.tr
                      key={row.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.2, delay: idx * 0.02 }}
                      className={cn(
                        "border-b border-border/25 transition-colors",
                        "hover:bg-surface-secondary/50 cursor-pointer"
                      )}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <td key={cell.id} className="px-4 py-2.5 text-sm">
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </td>
                      ))}
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile: Card mode with expandable rows */}
            <div className="sm:hidden divide-y divide-border-light">
              {table.getRowModel().rows.map((row, idx) => {
                const cells = row.getVisibleCells()
                const rankCell = cells.find(c => c.column.id === 'rank')
                const idCell = cells.find(c => c.column.id === 'candidateId')
                const scoreCell = cells.find(c => c.column.id === 'score')
                const badgeCell = cells.find(c => c.column.id === 'badge')
                const reasonCell = cells.find(c => c.column.id === 'reasoning')
                const isExpanded = expandedCards.has(idx)
                return (
                  <motion.div
                    key={row.id}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2, delay: idx * 0.03 }}
                  >
                    <button
                      onClick={() => toggleCard(idx)}
                      className="w-full p-3 active:bg-surface-secondary transition-colors text-left"
                      aria-expanded={isExpanded}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {rankCell && flexRender(rankCell.column.columnDef.cell, rankCell.getContext())}
                          {idCell && flexRender(idCell.column.columnDef.cell, idCell.getContext())}
                        </div>
                        <div className="flex items-center gap-2">
                          {badgeCell && flexRender(badgeCell.column.columnDef.cell, badgeCell.getContext())}
                          {scoreCell && (
                            <span className="font-mono text-sm font-bold text-brand-600">
                              {flexRender(scoreCell.column.columnDef.cell, scoreCell.getContext())}
                            </span>
                          )}
                        </div>
                      </div>
                      {reasonCell && (
                        <p className={cn(
                          "text-[11px] text-text-muted transition-all duration-200",
                          !isExpanded && "line-clamp-2"
                        )}>
                          {flexRender(reasonCell.column.columnDef.cell, reasonCell.getContext())}
                        </p>
                      )}
                      {reasonCell && isExpanded && (
                        <span className="text-[10px] text-brand-500 mt-1 block">Tap to collapse</span>
                      )}
                    </button>
                  </motion.div>
                )
              })}
            </div>
      </motion.div>

      {/* Pagination */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2">
        <p className="text-xs text-text-muted">
          Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}
          {" to "}
          {Math.min(
            (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
            data.length
          )}{" "}
          of {data.length} candidates
        </p>
        <div className="flex gap-1">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft className="w-3.5 h-3.5" />
          </Button>
          {Array.from({ length: Math.min(table.getPageCount(), 7) }, (_, i) => (
            <Button
              key={i}
              variant={table.getState().pagination.pageIndex === i ? "default" : "outline"}
              size="sm"
              className={cn(
                "min-w-[32px]",
                table.getState().pagination.pageIndex === i && "pointer-events-none"
              )}
              onClick={() => table.setPageIndex(i)}
            >
              {i + 1}
            </Button>
          ))}
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>
    </div>
  )
}

export default RankingsPage
