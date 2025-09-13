export default {
  "app": {
    "title": "MixTeX OCR - 图片转数学公式"
  },
  header: {
    title: 'MixTeX OCR',
    downloadModel: '下载并设置模型',
    closeApp: '关闭应用',
    alternativeLanguage: "Lang"
  },
  download: {
    title: "下载模型",
    confirmMessage: "将自动从GitHub下载MixTeX模型文件并设置。此过程可能需要几分钟时间，取决于您的网络速度。",
    confirmButton: "确认下载",
    cancelButton: "取消",
    downloading: "正在下载模型文件...",
    downloadSuccess: "模型下载并设置成功！",
    downloadFailed: "下载模型失败",
    downloadError: "模型下载失败"
  },
  clipboard: {
    title: '图片识别',
    pasteHint: '按 Ctrl+V 粘贴图片',
    dragHint: '或者直接拖拽图片到此区域',
    formatSettings: '输出格式设置',
    useDollars: '使用 $ 符号包围行内公式',
    convertAlign: '转换align环境为单行公式 $$',
    useTypst: '输出为 Typst'
  },
  messages: {
    recognizing: '正在识别图片中的数学公式...',
    recognizeImage: '识别图片',
    recognitionResult: '识别结果',
    recognitionNoResult: '暂无识别结果',
    recognitionSuccess: '识别成功',
    recognitionFailed: '识别失败',
    pleaseSelectImage: '请先选择图片',
    invalidImageFile: '请选择图片文件',
    uploadReminder: '请在左侧上传或粘贴图片进行识别',
    processingError: '处理图片时出错: ',
    requestFailed: '请求失败: ',
    noImageToReReognize: '没有可重新识别的图片',
    appClosing: '正在关闭应用...',
    appClosed: '应用已关闭',
    operationFailed: '操作失败: ',
    copiedToClipboard: "已复制到剪贴板",
    feedbackSubmitted: "反馈已提交成功",
    feedbackFailed: "反馈提交失败",
    languageChanged: '语言已切换',
  },
  buttons: {
    copyResult: "复制结果",
    reRecognize: "重新识别",
    perfect: "完美", 
    mistake: "失误"
  },
  dialogs: {
    confirmClose: '确定要关闭应用吗？',
    closeApp: '关闭应用',
    confirm: '确认',
    cancel: '取消'
  },
  footer: {
    poweredBy: '由 MixTeX OCR 提供技术支持',
    about: '关于',
    projectLink: '访问项目主页'
  },
  about: {
    title: '关于 MixTeX OCR',
    webVersion: 'MixTeX OCR 网页版',
    techStack: '技术栈',
    frontend: '前端',
    backend: '后端',
    model: '模型',
    modelText: '模型',
    typst: 'Typst 格式支持',
    rebuilders: '网站版重构者',
    originalAuthor: '原作者',
    credits: '贡献者',
    and: '和'
  }
}