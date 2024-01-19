import { toast } from "react-toastify";

export const requestError = (message) => toast.error(message);

export const requestSuccess = (message) => toast.success(message);
