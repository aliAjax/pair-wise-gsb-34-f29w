import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

interface ToastState {
  message: string;
  severity: "success" | "error" | "info" | "warning";
}

const ToastContext = createContext<{
  notify: (message: string, severity?: ToastState["severity"]) => void;
  notifyError: (error: unknown) => void;
}>({ notify: () => undefined, notifyError: () => undefined });

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<ToastState | null>(null);

  const notify = useCallback(
    (message: string, severity: ToastState["severity"] = "info") => setToast({ message, severity }),
    []
  );
  const notifyError = useCallback((error: unknown) => {
    const message = error instanceof Error ? error.message : "操作失败";
    setToast({ message, severity: "error" });
  }, []);

  const value = useMemo(() => ({ notify, notifyError }), [notify, notifyError]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <Snackbar
        open={toast !== null}
        autoHideDuration={4000}
        onClose={() => setToast(null)}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        {toast ? <Alert severity={toast.severity} onClose={() => setToast(null)}>{toast.message}</Alert> : undefined}
      </Snackbar>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
