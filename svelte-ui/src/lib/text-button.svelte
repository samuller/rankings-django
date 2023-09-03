<!--
  @component
  Make a clickable text button that handles accessibility by allowing both click and keyboard action.
  See: https://svelte.dev/docs/accessibility-warnings#a11y-click-events-have-key-events

  Usage:
  ```tsx
  <TextButton on:click={window.refresh}>Refresh</TextButton>
  ```
-->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    function triggerPress() {
        dispatch('click', {});
    }
</script>

<span class="underline" on:click={triggerPress} on:keyup={triggerPress} tabindex="0" role="button">
    <slot></slot>
</span>
