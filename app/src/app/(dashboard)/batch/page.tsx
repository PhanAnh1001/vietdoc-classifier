"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  createBatch,
  getBatchStatus,
  type BatchJobResponse,
  type BatchJobDetail,
  type BatchDocumentResult,
} from "@/lib/api";
import { Upload, Loader2, CheckCircle, XCircle, Clock } from "lucide-react";

const STATUS_ICON = {
  done: <CheckCircle className="h-4 w-4 text-green-500" />,
  failed: <XCircle className="h-4 w-4 text-red-500" />,
  processing: <Loader2 className="h-4 w-4 animate-spin text-blue-500" />,
  pending: <Clock className="h-4 w-4 text-muted-foreground" />,
};

function DocRow({ doc }: { doc: BatchDocumentResult }) {
  return (
    <div className="flex items-center gap-3 py-2 border-b last:border-0 text-sm">
      <div className="shrink-0">
        {STATUS_ICON[doc.status as keyof typeof STATUS_ICON] ?? STATUS_ICON.pending}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate">{doc.filename}</p>
        {doc.error_msg && (
          <p className="text-xs text-red-500 truncate">{doc.error_msg}</p>
        )}
      </div>
      {doc.doc_type_label && (
        <div className="text-right shrink-0">
          <p className="text-xs font-medium">{doc.doc_type_label}</p>
          {doc.confidence !== null && (
            <p className="text-xs text-muted-foreground">
              {(doc.confidence * 100).toFixed(0)}%
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function BatchPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [job, setJob] = useState<BatchJobResponse | null>(null);
  const [jobDetail, setJobDetail] = useState<BatchJobDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Poll for status while job is running
  useEffect(() => {
    if (!job) return;
    if (["done", "failed"].includes(job.status)) return;

    pollRef.current = setInterval(async () => {
      try {
        const detail = await getBatchStatus(job.job_id);
        setJobDetail(detail);
        setJob((prev) =>
          prev ? { ...prev, status: detail.status, processed: detail.processed, failed: detail.failed } : prev
        );
        if (["done", "failed"].includes(detail.status)) {
          clearInterval(pollRef.current!);
        }
      } catch {
        // ignore poll errors
      }
    }, 2000);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [job?.job_id, job?.status]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []);
    setFiles(selected);
    setError(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files);
    setFiles(dropped);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!files.length) return;
    setLoading(true);
    setError(null);
    setJob(null);
    setJobDetail(null);
    try {
      const res = await createBatch(files);
      setJob(res);
      // Immediately fetch status
      const detail = await getBatchStatus(res.job_id);
      setJobDetail(detail);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFiles([]);
    setJob(null);
    setJobDetail(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
    if (pollRef.current) clearInterval(pollRef.current);
  };

  const progress = job && job.total > 0 ? (job.processed / job.total) * 100 : 0;

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold">Xử lý hàng loạt</h1>
        <p className="text-muted-foreground mt-1">
          Upload tối đa 50 file JPG/PNG/PDF cùng lúc.
        </p>
      </div>

      {!job && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Upload files</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => inputRef.current?.click()}
              className="cursor-pointer rounded-lg border-2 border-dashed border-muted-foreground/30 p-8 text-center hover:border-muted-foreground/60 transition-colors"
            >
              <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
              {files.length > 0 ? (
                <div>
                  <p className="font-medium">{files.length} file được chọn</p>
                  <p className="text-xs text-muted-foreground">
                    {files.map((f) => f.name).join(", ").slice(0, 80)}
                    {files.map((f) => f.name).join(", ").length > 80 ? "..." : ""}
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-sm font-medium">Kéo thả files vào đây</p>
                  <p className="text-xs text-muted-foreground">hoặc click để chọn nhiều file</p>
                </div>
              )}
              <input
                ref={inputRef}
                type="file"
                accept=".jpg,.jpeg,.png,.pdf"
                multiple
                className="hidden"
                onChange={handleFileChange}
              />
            </div>

            <div className="flex gap-3">
              <Button onClick={handleSubmit} disabled={!files.length || loading} className="flex-1">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Đang tạo batch...
                  </>
                ) : (
                  `Xử lý ${files.length > 0 ? files.length + " file" : ""}`
                )}
              </Button>
              {files.length > 0 && (
                <Button variant="outline" onClick={handleReset}>Xóa</Button>
              )}
            </div>

            {error && (
              <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                {error}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Job status */}
      {job && (
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">
                Batch job{" "}
                <span className="font-mono text-xs text-muted-foreground">{job.job_id.slice(0, 8)}</span>
              </CardTitle>
              <Button size="sm" variant="ghost" onClick={handleReset}>
                Tạo batch mới
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Progress */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>
                  {job.processed}/{job.total} đã xử lý
                  {job.failed > 0 && <span className="text-red-500 ml-1">({job.failed} lỗi)</span>}
                </span>
                <span
                  className={
                    job.status === "done"
                      ? "text-green-600 font-medium"
                      : job.status === "failed"
                      ? "text-red-600 font-medium"
                      : "text-blue-600"
                  }
                >
                  {job.status}
                </span>
              </div>
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    job.status === "done" ? "bg-green-500" : "bg-blue-500"
                  }`}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Document list */}
            {jobDetail && jobDetail.results.length > 0 && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">Kết quả từng file</p>
                <div className="rounded-md border divide-y">
                  {jobDetail.results.map((doc) => (
                    <div key={doc.id} className="px-3">
                      <DocRow doc={doc} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
