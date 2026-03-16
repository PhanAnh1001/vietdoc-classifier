"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ClassifyResult } from "@/lib/api";

interface Props {
  result: ClassifyResult;
}

const CONFIDENCE_COLOR = (c: number) =>
  c >= 0.9 ? "text-green-600" : c >= 0.7 ? "text-yellow-600" : "text-red-600";

export function ClassifyResultCard({ result }: Props) {
  const metaEntries = Object.entries(result.metadata || {}).filter(
    ([, v]) => v !== null && v !== undefined && v !== "",
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Kết quả phân loại</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Doc type + confidence */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs text-muted-foreground mb-0.5">Loại chứng từ</p>
            <p className="text-xl font-bold">{result.doc_type_label}</p>
            <p className="text-xs text-muted-foreground font-mono">{result.doc_type}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-muted-foreground mb-0.5">Độ tin cậy</p>
            <p className={`text-2xl font-bold ${CONFIDENCE_COLOR(result.confidence)}`}>
              {(result.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Filename */}
        <div>
          <p className="text-xs text-muted-foreground">Tên file</p>
          <p className="text-sm font-medium truncate">{result.filename}</p>
        </div>

        {/* Metadata */}
        {metaEntries.length > 0 && (
          <div>
            <p className="text-xs text-muted-foreground mb-2">Dữ liệu trích xuất</p>
            <div className="rounded-md bg-muted/50 p-3 space-y-1">
              {metaEntries.map(([key, val]) => (
                <div key={key} className="flex gap-2 text-sm">
                  <span className="text-muted-foreground min-w-[140px] shrink-0 font-mono text-xs">
                    {key}
                  </span>
                  <span className="font-medium break-all">{String(val)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* OCR text preview */}
        {result.ocr_text && (
          <details className="text-sm">
            <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
              Nội dung OCR ({result.ocr_text.length} ký tự)
            </summary>
            <pre className="mt-2 max-h-40 overflow-auto rounded bg-muted/50 p-3 text-xs whitespace-pre-wrap">
              {result.ocr_text}
            </pre>
          </details>
        )}
      </CardContent>
    </Card>
  );
}
