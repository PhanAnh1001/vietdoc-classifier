"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { FileSearch, Layers, BarChart2 } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <p className="text-muted-foreground">
        Hệ thống phân loại chứng từ kế toán và ngân hàng tiếng Việt.
      </p>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <FileSearch className="h-4 w-4" />
              Phân loại đơn lẻ
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm">Upload 1 file JPG/PNG/PDF, nhận kết quả ngay lập tức.</p>
            <Button asChild size="sm" className="w-full">
              <Link href="/classify">Bắt đầu</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Layers className="h-4 w-4" />
              Xử lý hàng loạt
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm">Upload tối đa 50 file, xử lý bất đồng bộ.</p>
            <Button asChild size="sm" variant="outline" className="w-full">
              <Link href="/batch">Upload batch</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <BarChart2 className="h-4 w-4" />
              Đánh giá mô hình
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm">Xem accuracy và F1-score trên test set.</p>
            <Button asChild size="sm" variant="outline" className="w-full">
              <Link href="/evaluate">Xem metrics</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-3">12 loại chứng từ được hỗ trợ</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
          {[
            "Hóa đơn VAT đầu vào",
            "Hóa đơn VAT đầu ra",
            "Phiếu chi",
            "Phiếu thu",
            "Sao kê ngân hàng",
            "Giấy ủy quyền",
            "Thông báo công nợ",
            "Thông báo ghi có",
            "Biên lai",
            "Hợp đồng",
            "Phiếu kế toán",
            "Bảng lương",
          ].map((t) => (
            <div key={t} className="flex items-center gap-2 text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-500 inline-block" />
              {t}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
