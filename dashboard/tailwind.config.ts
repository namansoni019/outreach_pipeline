import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#3B18D6', // the deep purple seen in the design
          hover: '#2D12A6',
          muted: 'rgba(59, 24, 214, 0.08)',
          light: '#5A45FF',
        },
        surface: {
          base: '#F4F5F7', // very light grey for main bg
          sidebar: '#FFFFFF',
          card: '#FFFFFF',
          border: '#E2E8F0', // standard slate-200
          hover: '#F8FAFC',
        },
        ink: {
          primary: '#0F172A', // slate-900
          secondary: '#64748B', // slate-500
          muted: '#94A3B8', // slate-400
        },
        status: {
          success: '#10B981', // green
          successbg: 'rgba(16, 185, 129, 0.1)',
          pending: '#6366F1', // indigo
          pendingbg: 'rgba(99, 102, 241, 0.1)',
          danger: '#EF4444', // red
          dangerbg: 'rgba(239, 68, 68, 0.1)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'card': '0px 1px 3px rgba(0, 0, 0, 0.05), 0px 4px 6px rgba(0, 0, 0, 0.02)',
        'sidebar': '1px 0px 10px rgba(0, 0, 0, 0.03)',
      }
    },
  },
  plugins: [],
};
export default config;
