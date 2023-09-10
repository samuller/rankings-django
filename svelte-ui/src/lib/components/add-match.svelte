<script lang="ts">
	import Tabs from "./tabs.svelte";

    const teams = ["Team 1", "Team 2"];
    const members = [["Player 1", "Player 2"], ["Player 3", "Player 4"]];

    let multiMatchWins: number[] = [1, 2, 1];
    const addMultiMatchTeam = function (teamNr: number) {
        multiMatchWins.push(teamNr);
        // multiMatchWins = multiMatchWins;
    };
</script>


<h3 class="font-bold text-2xl">Match results</h3>
<p class="pt-4">Specify the teams that played:</p>

<div>
    {#each teams as team, teamIdx}
    <table class="table">
        <thead>
          <tr class="bg-base-200">
            <th class="text-center text-white text-lg">{team}</th>
          </tr>
        </thead>
        <tbody>
          <tr class="flex flex-col sm:flex-row">
              {#each members[teamIdx] as member}
              <select class="flex-1 m-1 sm:m-3 select select-bordered sm:max-w-xs">
                  <option disabled selected>[{member}]</option>
                  <option>Han Solo</option>
                  <option>Greedo</option>
              </select>
              {/each}
          </tr>
        </tbody>
    </table>
    {/each}
    <Tabs data={[
        { title: "Single Match", id: "single-match" },
        { title: "Multiple Matches", id: "multi-match" },
        { title: "Round-Tobin Teams", id: "round-robin" },
    ]}>
        <div id="single-match">
            <p class="pt-4">Select the winning team for a single game:</p>
            <div class="flex flex-col sm:flex-row gap-6">
                <button class="btn btn-primary flex-1">Team 1</button>
                <button class="btn btn-primary flex-1">Team 2</button>
            </div>
        </div>

        <div id="multi-match">
            <p class="pt-4">
                Select the results for multiple games (between the same teams):
            </p>
            <div class="flex flex-row gap-6">
                <div class="flex-1 flex flex-col gap-6">
                    <button class="btn flex-1" on:click={() => addMultiMatchTeam(1)}>Team 1</button>
                    <button class="btn flex-1" on:click={() => addMultiMatchTeam(2)}>Team 2</button>
                </div>
                <div class="flex-1">
                    <select id="multi-match-list" multiple size={8} class="w-full h-full">
                        {#each multiMatchWins as matchWinner,idx}
                            <option value={idx}>Team {matchWinner} win</option>
                        {/each}
                    </select>
                </div>
                <div class="flex-1 flex flex-col gap-6">
                    <button class="btn btn-neutral flex-1">Remove selected</button>
                    <button class="btn btn-primary flex-1">Submit</button>
                </div>
            </div>
        </div>

        <div id="round-robin">
            <p class="pt-4">Select a result for a set of games consisting of all team combinations:</p>
            <div class="flex flex-col items-center">
                <span class="flex flex-row items-baseline">
                    <p>Won 3 games:</p>
                    <select class="flex-1 m-1 sm:m-3 select select-bordered sm:max-w-xs">
                        <option selected>(None)</option>
                        <option>Han Solo</option>
                        <option>Greedo</option>
                    </select>
                </span>
                <span class="flex flex-row items-baseline">
                    <p>Lost 3 games:</p>
                    <select class="flex-1 m-1 sm:m-3 select select-bordered sm:max-w-xs">
                        <option selected>(None)</option>
                        <option>Han Solo</option>
                        <option>Greedo</option>
                    </select>
                </span>
                <button class="btn btn-primary flex-1 md:w-1/2">Submit</button>
            </div>
        </div>
    </Tabs>
</div>