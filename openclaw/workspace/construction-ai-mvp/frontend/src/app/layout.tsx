export const metadata = {
  title: 'Construction AI MVP',
  description: 'ระบบ AI บริหารโครงการก่อสร้าง',
}

export default function RootLayout({ children }) {
  return (
    <html lang="th">
      <body>{children}</body>
    </html>
  )
}
