import { Button } from "@/components/livekit/button";

//
// ICONS
//
function SecurityPulseIcon() {
  return (
    <div className="relative mb-8">
      {/* Glow circle */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="h-28 w-28 rounded-full bg-emerald-500/10 animate-ping"></div>
      </div>

      {/* Shield */}
      <div className="relative flex items-center justify-center">
        <svg
          className="h-20 w-20 text-emerald-400 drop-shadow-lg"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.5}
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 6.75L4.5 9v3c0 4.28 3.06 8.32 7.5 9.75 4.44-1.43 7.5-5.47 7.5-9.75V9l-7.5-2.25z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M9.75 12l1.5 1.5 3-3"
          />
        </svg>
      </div>
    </div>
  );
}

function SmallIcon({ children }: { children: React.ReactNode }) {
  return <div className="h-4 w-4 text-emerald-400">{children}</div>;
}

//
// MAIN WELCOME VIEW
//
interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<"div"> & WelcomeViewProps) => {
  return (
    <div
      ref={ref}
      className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white"
    >
      <section className="flex flex-col items-center justify-center text-center px-6 py-16">
        {/* Icon */}
        <SecurityPulseIcon />

        {/* Title */}
        <h1 className="text-4xl font-extrabold tracking-tight mb-2 text-emerald-400 drop-shadow">
          SecureBank Assist
        </h1>

        <p className="text-slate-400 text-sm mb-8">
          AI-powered security verification • 24/7 protection
        </p>

        {/* Info Box */}
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-5 max-w-md mb-8 backdrop-blur-sm shadow-md">
          <div className="border-l-4 border-red-500 bg-red-900/20 p-4 rounded-md">
  <p className="text-red-200 leading-relaxed">
    ⚠️ A recent transaction requires your <span className="text-red-400 font-semibold">urgent verification</span>.  
    Connect with our secure AI assistant to confirm your activity and ensure your account remains safe.
  </p>
</div>


        </div>

        {/* Start Button */}
        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="w-72 py-3 font-semibold text-lg bg-emerald-600 hover:bg-emerald-700 shadow-lg shadow-emerald-900/40"
        >
          {startButtonText}
        </Button>

        {/* Security Badges */}
        <div className="mt-10 flex items-center gap-10 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <SmallIcon>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  d="M12 6.75L4.5 9v3c0 4.28 3.06 8.32 7.5 9.75 4.44-1.43 7.5-5.47 7.5-9.75V9l-7.5-2.25z"
                  strokeWidth={1.8}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </SmallIcon>
            <span>Bank-grade Security</span>
          </div>

          <div className="flex items-center gap-2">
            <SmallIcon>
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </SmallIcon>
            <span>256-bit Encryption</span>
          </div>
        </div>
      </section>
    </div>
  );
};
