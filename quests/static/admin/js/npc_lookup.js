(function($) {
    $(document).ready(function() {
        // Function to handle the selection of an NPC from the popup
        window.handleNPCSelection = function(id, name) {
            // Set the value in the starting_npc_id field
            $('#id_starting_npc_id').val(id);

            // Update the display to show the selected NPC name
            const displayElement = $('#npc_display');
            if (displayElement.length) {
                displayElement.text(name + ' (' + id + ')');
            } else {
                // Create display element if it doesn't exist
                $('#id_starting_npc_id').after(
                    '<span id="npc_display" style="margin-left: 10px; font-style: italic;">' +
                    name + ' (' + id + ')</span>'
                );
            }

            // Close the popup
            window.close();
        };

        // Add click handlers for the lookup buttons in related NPCs inline
        $('.add-related-npc').on('click', function(e) {
            e.preventDefault();
            const url = $(this).data('url');
            const targetId = $(this).data('target');

            // Open popup to search NPCs
            const popup = window.open(url, 'npcPopup', 'width=800,height=600');

            // Store the target field id for later use when selection is made
            window.currentNPCTargetId = targetId;

            return false;
        });
    });
})(django.jQuery);