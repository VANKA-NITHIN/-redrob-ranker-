import { useState, useMemo, useCallback } from "react"
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
import { cn, formatScore } from "@/lib/utils"
import {
  Search,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Trophy,
  Star,
  Filter,
  Download,
} from "lucide-react"

interface RankingRow {
  rank: number
  score: number
  candidateId: string
  reasoning: string
  badge: "verified" | "suspicious" | "honeypot"
}

const columnHelper = createColumnHelper<RankingRow>()

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
    cell: (info) => (
      <span className="font-mono text-sm text-text-primary">
        {info.getValue()}
      </span>
    ),
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

// Generate mock data matching our sample output
function generateMockData(): RankingRow[] {
  const data: RankingRow[] = []
  const candidates = [
    { id: "CAND_0000031", score: 0.7621, badge: "suspicious" as const, reasoning: "SUSPICIOUS PROFILE (7 AI skills not evidenced; statistical anomaly in description length); Data Scientist; 11yrs ..." },
    { id: "CAND_0000001", score: 0.1818, badge: "suspicious" as const, reasoning: "SUSPICIOUS PROFILE (7 AI skills not evidenced); Backend Engineer; 7yrs at Mindtree; product co; responsive; actively looking; short notice ..." },
    { id: "CAND_0000010", score: 0.1496, badge: "verified" as const, reasoning: "ML Engineer; 7yrs at Zomato; built ranking, recommendation, retrieval systems; product co; responsive; actively looking; short notice; based Bengaluru ..." },
    { id: "CAND_0000023", score: 0.1302, badge: "verified" as const, reasoning: "Software Engineer; 8yrs at Google; built search infrastructure components ..." },
    { id: "CAND_0000044", score: 0.1197, badge: "verified" as const, reasoning: "Data Scientist; 6yrs at Amazon; worked on recommendation systems ..." },
    { id: "CAND_0000048", score: 0.1151, badge: "verified" as const, reasoning: "ML Engineer; 5yrs at Microsoft; built production ML pipelines ..." },
    { id: "CAND_0000027", score: 0.1113, badge: "verified" as const, reasoning: "AI Engineer; 9yrs at LinkedIn; worked on search relevance ..." },
    { id: "CAND_0000024", score: 0.0844, badge: "verified" as const, reasoning: "Software Engineer; 7yrs; product co experience ..." },
    { id: "CAND_0000016", score: 0.0684, badge: "verified" as const, reasoning: "Full Stack Engineer; 6yrs; building data pipelines ..." },
    { id: "CAND_0000032", score: 0.0664, badge: "suspicious" as const, reasoning: "SUSPICIOUS PROFILE (salary range inverted; statistical anomaly); ..." },
  ]

  // Extend to 50 entries
  for (let i = 0; i < 50; i++) {
    const base = candidates[i % candidates.length]
    data.push({
      rank: i + 1,
      score: base.score * (1 - i * 0.002),
      candidateId: i < candidates.length ? candidates[i].id : `CAND_${String(i + 1).padStart(7, "0")}`,
      reasoning: base.reasoning,
      badge: i < 3 ? base.badge : (i < 45 ? "verified" : "suspicious"),
    })
  }
  return data
}

export function RankingsPage() {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState("")
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set())

  const toggleCard = useCallback((idx: number) => {
    setExpandedCards((prev) => {
      const next = new Set(prev)
      if (next.has(idx)) next.delete(idx)
      else next.add(idx)
      return next
    })
  }, [])

  const data = useMemo(() => generateMockData(), [])

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

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-fluid-section font-semibold text-text-primary">
              Candidate Rankings
            </h2>
            <p className="text-fluid-small text-text-muted mt-0.5">
              AI-powered ranking of {data.length} candidates
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Filter className="w-3.5 h-3.5 mr-1.5" />
              Filters
            </Button>
            <Button variant="gradient" size="sm">
              <Download className="w-3.5 h-3.5 mr-1.5" />
              Export
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Top 3 Highlight */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="grid-auto-responsive gap-3"
      >
        {data.slice(0, 3).map((c, i) => (
          <Card key={c.candidateId} hover>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className={cn(
                  "w-10 h-10 rounded-[10px] flex items-center justify-center text-lg font-bold",
                  i === 0 ? "bg-amber-50 text-amber-600" :
                  i === 1 ? "bg-slate-50 text-slate-500" :
                  "bg-orange-50 text-orange-600"
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
                  <p className="text-xs text-text-muted truncate mt-0.5">
                    {c.reasoning}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-mono text-lg font-bold text-brand-600">
                    {formatScore(c.score)}
                  </p>
                  <p className="text-[10px] text-text-dim uppercase tracking-wider">
                    Score
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Search + Filter Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-text-dim" />
          <input
            type="text"
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Search by ID, company, or skill..."
            className="w-full h-9 pl-9 pr-3 rounded-[8px] border border-border/50 bg-surface-secondary text-xs text-text-primary placeholder:text-text-dim focus:outline-none focus:border-brand-300 focus:ring-1 focus:ring-brand-200 transition-all"
          />
        </div>
        <select className="h-9 px-3 rounded-[8px] border border-border/50 bg-surface-secondary text-xs text-text-muted focus:outline-none">
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
      >
        <Card>
          <CardContent className="p-0">
            {/* Desktop: Full table */}
            <div className="hidden sm:block overflow-x-auto">
              <table className="w-full">
                <thead>
                  {table.getHeaderGroups().map((headerGroup) => (
                    <tr key={headerGroup.id} className="border-b border-border/50">
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
            <div className="sm:hidden divide-y divide-border/25">
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
          </CardContent>
        </Card>
      </motion.div>

      {/* Pagination */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
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
          {Array.from({ length: table.getPageCount() }, (_, i) => (
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
