// 先定义 isEmpty，确保在 hasEmptyValues 中可用
export const isEmpty = (value) => {
  return value === null || 
         value === undefined || 
         value === '' || 
         (Array.isArray(value) && value.length === 0) ||
         (typeof value === 'string' && value.trim() === '');
};

export const hasEmptyValues = (array, keys = []) => {
  if (!Array.isArray(array)) return false;
  
  for (const item of array) {
    // 如果指定了检查的字段
    if (keys.length > 0) {
      for (const key of keys) {
        // 修正：去掉 this
        if (isEmpty(item[key])) {
          return true;
        }
      }
    } else {
      // 检查对象的所有值
      for (const key in item) {
        // 修正：去掉 this
        if (isEmpty(item[key])) {
          return true;
        }
      }
    }
  }
  return false;
};