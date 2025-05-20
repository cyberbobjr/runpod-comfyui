// Directive pour des tooltips améliorés avec Tippy.js
export const tooltip = {
  mounted(el, binding) {
    const content = binding.value || el.getAttribute('title');
    if (!content) return;
    
    // Supprimer l'attribut title natif pour éviter les tooltips doubles
    el.removeAttribute('title');
    
    // Options par défaut
    const defaultOptions = {
      content,
      theme: 'light',
      placement: 'top',
      animation: 'scale',
      arrow: true,
      duration: [300, 250],
      delay: [300, 0],
      maxWidth: 300
    };
    
    // Fusionner avec les options personnalisées si elles sont fournies
    const options = typeof binding.value === 'object' 
      ? { ...defaultOptions, ...binding.value } 
      : defaultOptions;
    
    // Initialiser Tippy sur l'élément
    const instance = tippy(el, options);
    
    // Stocker l'instance pour pouvoir la manipuler plus tard
    el._tippy = instance;
  },
  
  updated(el, binding) {
    // Mettre à jour le contenu du tooltip si la valeur change
    if (el._tippy) {
      const content = typeof binding.value === 'object' 
        ? binding.value.content 
        : binding.value;
        
      if (content && content !== el._tippy.props.content) {
        el._tippy.setContent(content);
      }
    }
  },
  
  beforeUnmount(el) {
    // Nettoyer l'instance Tippy lorsque l'élément est supprimé
    if (el._tippy) {
      el._tippy.destroy();
    }
  }
};
