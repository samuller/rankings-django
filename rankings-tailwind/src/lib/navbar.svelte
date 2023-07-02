<script lang="ts">
    let navMenuOpen = false;
    let requestMenuOpen = false;
</script>

<nav class="w-full bg-gray-600 text-white border-b border-gray-200 flex flex-wrap items-center justify-between p-4">
    <a href="/" class="font-medium flex items-center">
        Rankings
    </a>
    <button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 ml-3 text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200" aria-controls="navbar-default"
        on:click={() => navMenuOpen = !navMenuOpen}
        aria-expanded="false">
        <span class="sr-only">Open main menu</span>
        <svg class="w-6 h-6" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>
    </button>
    <div class:hidden={!navMenuOpen} class="w-full md:block md:w-auto" id="navbar-default">
        <ul class="flex flex-col p-4 md:p-0 mt-4 border rounded-lg md:flex-row md:space-x-8 md:mt-0 md:border-0 bg-slate-500 md:bg-transparent">
            <li>
                <button id="dropdownNavbarLink"
                    data-dropdown-toggle="dropdownNavbar"
                    class="w-full py-2 pl-3 pr-4 rounded hover:bg-gray-600 md:hover:bg-transparent md:hover:text-gray-500 md:p-0 flex items-center justify-between"
                    on:click={() => requestMenuOpen = !requestMenuOpen}
                    on:blur={() => requestMenuOpen = false} tabindex="0">
                    Request
                    <svg class="w-5 h-5 ml-1" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                </button>
                <!-- Dropdown menu -->
                <div id="dropdownNavbar" class:hidden={!requestMenuOpen}
                    class="relative md:absolute z-10 font-normal text-sm divide-y divide-gray-600 rounded-lg shadow w-44 bg-gray-700">
                    <div class="py-1">
                        <a href="#" class="block px-4 py-2 hover:bg-gray-600 hover:text-white">
                            Clear submission
                        </a>
                    </div>
                    <ul class="py-2" aria-labelledby="dropdownLargeButton">
                      <li>
                        <a href="#" class="block px-4 py-2 hover:bg-gray-600 hover:text-white">
                            New player
                        </a>
                      </li>
                      <li>
                        <a href="#" class="block px-4 py-2 hover:bg-gray-600 hover:text-white">
                            New tournament
                        </a>
                      </li>
                      <li>
                        <a href="#" class="block px-4 py-2 hover:bg-gray-600 hover:text-white">
                            New activity
                        </a>
                      </li>
                    </ul>
                </div>
            </li>
            <li>
                <a href="/about" class="block py-2 pl-3 pr-4 rounded hover:bg-gray-600 md:hover:bg-transparent md:hover:text-gray-500 md:p-0">
                    About
                </a>
            </li>
        </ul>
    </div>
</nav>
