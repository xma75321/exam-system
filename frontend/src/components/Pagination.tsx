"use client";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  total: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

const PAGE_SIZE_OPTIONS = [10, 20, 50];

export default function Pagination({
  currentPage,
  totalPages,
  total,
  pageSize,
  onPageChange,
  onPageSizeChange,
}: PaginationProps) {
  if (totalPages <= 0) return null;

  const getPageNumbers = (): (number | "...")[] => {
    const pages: (number | "...")[] = [];
    const delta = 2;

    const left = Math.max(1, currentPage - delta);
    const right = Math.min(totalPages, currentPage + delta);

    if (left > 1) {
      pages.push(1);
      if (left > 2) pages.push("...");
    }

    for (let i = left; i <= right; i++) {
      pages.push(i);
    }

    if (right < totalPages) {
      if (right < totalPages - 1) pages.push("...");
      pages.push(totalPages);
    }

    return pages;
  };

  return (
    <div className="flex flex-col items-center gap-3 sm:flex-row sm:justify-between">
      <p className="text-sm text-gray-500">
        共 <span className="font-medium text-gray-700">{total}</span> 道题目
      </p>

      <div className="flex items-center gap-1">
        <button
          type="button"
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          上一页
        </button>

        {getPageNumbers().map((page, idx) =>
          page === "..." ? (
            <span key={`ellipsis-${idx}`} className="px-1 text-sm text-gray-400">
              ...
            </span>
          ) : (
            <button
              key={page}
              type="button"
              onClick={() => onPageChange(page)}
              className={`min-w-[32px] rounded-lg px-2 py-1.5 text-sm transition-colors ${
                page === currentPage
                  ? "bg-primary-600 font-medium text-white"
                  : "border border-gray-200 text-gray-600 hover:bg-gray-50"
              }`}
            >
              {page}
            </button>
          )
        )}

        <button
          type="button"
          disabled={currentPage >= totalPages}
          onClick={() => onPageChange(currentPage + 1)}
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          下一页
        </button>
      </div>

      <div className="flex items-center gap-2">
        <label htmlFor="page-size-select" className="text-sm text-gray-500">
          每页
        </label>
        <select
          id="page-size-select"
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className="rounded-lg border border-gray-200 bg-white px-2 py-1.5 text-sm text-gray-700 transition-colors hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        >
          {PAGE_SIZE_OPTIONS.map((size) => (
            <option key={size} value={size}>
              {size}条
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}