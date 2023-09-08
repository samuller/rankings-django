<script lang="ts">
    import { page } from '$app/stores';
    import { navTitle } from '../../store';

    /**
     * Close dropdown menu if it is currently open - use with on:blur to close on click-away.
     *
     * This function is only needed when you want to use DaisyUI's dropdown menu based on the <details> tag.
     * See: https://daisyui.com/components/dropdown/#dropdown-menu-using-details-tag
     */
    function closeMenuIfOpen(event: Event) {
        if (!(event?.target instanceof HTMLElement)) {
            return;
        }
        const target: HTMLElement = event?.target;
        if (target?.parentElement && target.parentElement.hasAttribute("open")) {
            target.click();
        }
    }
</script>


<div class="navbar bg-base-100">
    <div class="flex-1">
        <a href="/" class="btn btn-ghost normal-case text-xl text-white">
            Rankings
        </a>
        {#if $navTitle != ""}
        <div class="text-sm breadcrumbs">
            <ul>
                <li></li>
                <!--
                    We show a breadcrumb with only the high-level route to help orientate which category of
                    the site (activity in our) you are currently in (since all the lower-level views of the categories
                    look very similar).
                -->
                <li><a href={`/${$page.url.pathname.split('/')[1]}`}>{$navTitle}</a></li>
            </ul>
        </div>
        {/if}
    </div>
    <div class="flex-none">
        <ul class="menu menu-horizontal px-1">
            <!-- <li>
                <details class="dropdown">
                    <summary on:blur={closeMenuIfOpen}>
                        Request
                    </summary>
                    <ul class="dropdown-content bg-base-200 p-2 !mt-0">
                        <li><a href="#">Clear submission</a></li>
                        !-- <li><hr/></li> --
                        <li><a href="#">New player</a></li>
                        <li><a href="#">New tournament</a></li>
                        <li><a href="#">New activity</a></li>
                    </ul>
                </details>
            </li> -->
            <li>
                <a href="/about">
                    About
                </a>
            </li>
        </ul>
    </div>
</div>
