"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  LayoutDashboard,
  FileSearch,
  Layers,
  Settings,
  User,
  LogOut,
  BarChart2,
} from "lucide-react";
import { useAuthStore } from "@/lib/auth-store";
import { Toaster } from "@/components/ui/toaster";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/classify", label: "Phân loại", icon: FileSearch },
  { href: "/batch", label: "Hàng loạt", icon: Layers },
  { href: "/evaluate", label: "Đánh giá", icon: BarChart2 },
  { href: "/settings", label: "Cài đặt", icon: Settings },
  { href: "/profile", label: "Tài khoản", icon: User },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { clearAuth } = useAuthStore();

  const handleLogout = () => {
    clearAuth();
    router.push("/login");
  };

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r bg-muted/40 p-4">
        <div className="mb-8">
          <h2 className="text-lg font-bold">VietDoc Classifier</h2>
          <p className="text-xs text-muted-foreground">Phân loại chứng từ AI</p>
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent"
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto pt-8">
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent"
          >
            <LogOut className="h-4 w-4" />
            Đăng xuất
          </button>
        </div>
      </aside>
      <main className="flex-1 p-8">{children}</main>
      <Toaster />
    </div>
  );
}
