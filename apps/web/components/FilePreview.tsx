import type { FileUploadResponse } from "@/types/api";

export default function FilePreview({ file }: { file: FileUploadResponse }) {
  if (!file.preview_rows || file.preview_rows.length === 0) {
    return <p className="text-sm text-slate-500">No rows to preview.</p>;
  }
  return (
    <div className="overflow-x-auto rounded-md border bg-white">
      <table className="data-table">
        <thead>
          <tr>
            {file.headers.map((h, idx) => (
              <th key={idx}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {file.preview_rows.map((row, rowIdx) => (
            <tr key={rowIdx}>
              {file.headers.map((h, colIdx) => (
                <td key={colIdx} className="max-w-[420px] whitespace-pre-wrap break-words">
                  {row[h] === null || row[h] === undefined ? "" : String(row[h])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
