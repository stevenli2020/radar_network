export const storeItem = (itemName, Item) =>
  (window.localStorage[itemName] = Item);
export const clearItem = (itemName) => (window.localStorage[itemName] = "");
export const getItem = (itemName) =>
  window.localStorage[itemName] ? window.localStorage[itemName] : "";
