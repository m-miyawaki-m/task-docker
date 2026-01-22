/// <reference types="vite/client" />

declare module 'vuetify/styles' {
  const styles: string
  export default styles
}

declare module 'vuetify/components' {
  import type { Component } from 'vue'
  const components: Record<string, Component>
  export = components
}

declare module 'vuetify/directives' {
  import type { Directive } from 'vue'
  const directives: Record<string, Directive>
  export = directives
}
