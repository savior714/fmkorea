import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "FM Korea 투자 패턴 분석기",
    description: "FM Korea 게시물 수집 및 투자 패턴 분석 도구",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="ko" className="dark">
            <body>{children}</body>
        </html>
    );
}
