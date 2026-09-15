export default function SearchBar({ valeur, onChange, onSubmit }) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
      className="w-full max-w-2xl"
    >
      <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm shadow-slate-200/50 transition focus-within:border-brand-500 focus-within:ring-4 focus-within:ring-brand-100 dark:border-slate-700 dark:bg-slate-800 dark:shadow-none dark:focus-within:border-brand-500 dark:focus-within:ring-brand-500/20">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="h-5 w-5 flex-shrink-0 text-slate-400 dark:text-slate-500"
        >
          <circle cx="11" cy="11" r="7" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          value={valeur}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Docker, API REST, machine learning..."
          className="w-full bg-transparent text-lg text-slate-800 placeholder:text-slate-400 focus:outline-none dark:text-slate-100 dark:placeholder:text-slate-500"
        />
      </div>
    </form>
  );
}