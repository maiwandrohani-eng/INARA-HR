import Image from 'next/image'

export function InaraLogo({ className = "w-12 h-12" }: { className?: string }) {
  return (
    <div className={className}>
      <Image
        src="/logo.png"
        alt="INARA Logo"
        width={100}
        height={100}
        className="w-full h-full object-contain"
        priority
      />
    </div>
  )
}
