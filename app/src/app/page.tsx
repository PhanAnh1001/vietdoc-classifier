import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex flex-1 flex-col items-center justify-center px-4 py-24 text-center">
        <span className="mb-4 inline-block rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 ring-1 ring-blue-200">
          AI · Vietnamese Documents
        </span>
        <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-6xl">
          VietDoc Classifier
        </h1>
        <p className="mb-8 max-w-xl text-lg text-muted-foreground">
          Tự động phân loại chứng từ kế toán và ngân hàng tiếng Việt bằng AI.
          Hỗ trợ 12 loại chứng từ, độ chính xác ≥ 90%.
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/classify">Phân loại ngay</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/login">Đăng nhập</Link>
          </Button>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-3 max-w-3xl w-full text-left">
          <div className="rounded-lg border p-5">
            <div className="mb-2 text-2xl">📄</div>
            <h3 className="font-semibold mb-1">12 loại chứng từ</h3>
            <p className="text-sm text-muted-foreground">
              Hóa đơn VAT, phiếu chi/thu, sao kê, hợp đồng, bảng lương và nhiều hơn.
            </p>
          </div>
          <div className="rounded-lg border p-5">
            <div className="mb-2 text-2xl">⚡</div>
            <h3 className="font-semibold mb-1">Xử lý hàng loạt</h3>
            <p className="text-sm text-muted-foreground">
              Upload tối đa 50 file cùng lúc, xử lý bất đồng bộ với theo dõi trạng thái.
            </p>
          </div>
          <div className="rounded-lg border p-5">
            <div className="mb-2 text-2xl">🎯</div>
            <h3 className="font-semibold mb-1">Trích xuất metadata</h3>
            <p className="text-sm text-muted-foreground">
              Tự động lấy số hóa đơn, ngày tháng, mã số thuế, số tiền từ chứng từ.
            </p>
          </div>
        </div>
      </main>

      <footer className="border-t px-4 py-6 text-center text-xs text-muted-foreground">
        &copy; {new Date().getFullYear()} VietDoc Classifier
      </footer>
    </div>
  );
}
