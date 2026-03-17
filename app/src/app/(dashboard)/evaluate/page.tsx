"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getEvaluationMetrics, type EvaluateResult } from "@/lib/api";
import { Loader2 } from "lucide-react";

const F1_COLOR = (f1: number) =>
  f1 >= 0.9 ? "text-green-600" : f1 >= 0.75 ? "text-yellow-600" : "text-red-600";

export default function EvaluatePage() {
  const [result, setResult] = useState<EvaluateResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getEvaluationMetrics(100);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold">Đánh giá mô hình</h1>
        <p className="text-muted-foreground mt-1">
          Tính accuracy và F1-score từ các chứng từ đã được gán nhãn trong hệ thống.
        </p>
      </div>

      <div className="flex gap-3">
        <Button onClick={handleEvaluate} disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Đang tính toán...
            </>
          ) : (
            "Tính metrics"
          )}
        </Button>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {result && (
        <>
          {result.total_evaluated === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center text-muted-foreground">
                <p>Chưa có dữ liệu để đánh giá.</p>
                <p className="text-sm mt-1">
                  Cần có chứng từ với cột <code>ground_truth</code> được gán nhãn.
                </p>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Summary */}
              <div className="grid gap-4 md:grid-cols-3">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xs text-muted-foreground">Tổng mẫu</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold">{result.total_evaluated}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xs text-muted-foreground">Accuracy</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className={`text-3xl font-bold ${F1_COLOR(result.accuracy)}`}>
                      {(result.accuracy * 100).toFixed(1)}%
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xs text-muted-foreground">Macro F1</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className={`text-3xl font-bold ${F1_COLOR(result.macro_f1)}`}>
                      {result.macro_f1.toFixed(3)}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Per-class F1 */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">F1-score theo loại</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(result.per_class_f1)
                      .sort(([, a], [, b]) => b - a)
                      .map(([cls, f1]) => (
                        <div key={cls} className="flex items-center gap-3">
                          <span className="text-sm font-mono w-32 shrink-0 text-muted-foreground text-xs">
                            {cls}
                          </span>
                          <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                f1 >= 0.9
                                  ? "bg-green-500"
                                  : f1 >= 0.75
                                  ? "bg-yellow-500"
                                  : "bg-red-500"
                              }`}
                              style={{ width: `${f1 * 100}%` }}
                            />
                          </div>
                          <span className={`text-sm font-bold w-12 text-right ${F1_COLOR(f1)}`}>
                            {f1.toFixed(3)}
                          </span>
                          <span className="text-xs text-muted-foreground w-16 text-right">
                            {result.confusion_counts[cls]
                              ? `${result.confusion_counts[cls].correct}/${result.confusion_counts[cls].total}`
                              : ""}
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </>
      )}
    </div>
  );
}
