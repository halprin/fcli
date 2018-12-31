from .fcissue import FcIssue


class BacklogIssue(FcIssue):

    # Backlog workflow
    # Open -> Resolved (21)
    # Open -> Closed (31)
    # Open -> Ready for Refinement (201)
    # In Progress -> Open (41)
    # In Progress -> Closed (61)
    # In Progress -> Blocked (241)
    # In Progress -> Socialize (261)
    # In Progress -> Ready (291)
    # In Progress -> Resolved (51)
    # Resolved -> Closed (71)
    # Resolved -> Verified (81)
    # Resolved -> Reopened (91)
    # Verified -> Closed (101)
    # Verified -> Ready to Deploy (121)
    # Verified -> Reopened (191)
    # Ready to Deploy -> Closed (131)
    # Ready to Deploy -> Reopened (141)
    # Reopened -> Closed (161)
    # Reopened -> In Progress (171)
    # Reopened -> Resolved (51)
    # Closed -> Reopened (181)
    # Ready for Refinement -> Refined (211)
    # Ready for Refinement -> Needs Work (231)
    # Refined -> Ready (221)
    # Refined -> Needs Work (231)
    # Needs Work -> Ready for Refinement (201)
    # Ready -> In Progress (11)
    # Ready -> Needs Work (231)
    # Blocked -> In Progress (251)
    # Socialize -> In Progress (271)
    # Socialize -> Resolved (281)
    transition_dict = {
        'Open': {'Resolved': [21],  # Open -> Resolved
                 'Closed': [31],  # Open -> Closed
                 'Ready for Refinement': [201],  # Open -> RfR
                 'In Progress': [201, 211, 221, 11],  # Open -> RfR -> Refined -> Ready -> In Progress
                 'Needs Work': [201, 231],  # Open -> RfR -> Needs Work
                 'Refined': [201, 211],  # Open -> RfR -> Refined
                 'Ready': [201, 211, 221],  # Open -> RfR -> Refined -> Ready
                 'Blocked': [201, 211, 221, 11, 241],  # Open -> RfR -> Refined -> Ready -> IP -> Blocked
                 'Socialize': [201, 211, 221, 11, 261]},  # Open -> RfR -> Ref -> Ready -> IP -> Social
        'Ready for Refinement': {
                 'Resolved': [211, 221, 11, 51],  # RfR -> Refined -> Ready -> IP -> Resolved
                 'Closed': [211, 221, 11, 61],  # RfR -> Refined -> Ready -> IP -> Closed
                 'Open': [211, 221, 11, 41],  # RfR -> Refined -> Ready -> In Progress -> Open
                 'In Progress': [211, 221, 11],  # RfR -> Refined -> Ready -> In Progress
                 'Needs Work': [231],  # RfR -> Needs Work
                 'Refined': [211],  # RfR -> Refined
                 'Ready': [211, 221],  # RfR -> Refined -> Ready
                 'Blocked': [211, 221, 11, 241],  # RfR -> Refined -> Ready -> IP -> Block
                 'Socialize': [211, 221, 11, 261]},  # RfR -> Ref -> Ready -> IP -> Social
        'Needs Work': {
                 'Resolved': [201, 211, 221, 11, 51],  # NW -> RfR -> Refined -> Ready -> IP -> Res
                 'Closed': [201, 211, 221, 11, 61],  # NW -> RfR -> Refined -> Ready -> IP -> Closed
                 'Open': [201, 211, 221, 11, 41],  # NW -> RfR -> Refined -> Ready -> IP -> Open
                 'In Progress': [201, 211, 221, 11],  # Needs Work -> RfR -> Refined -> Ready -> IP
                 'Ready for Refinement': [201],  # Needs Work -> RfR
                 'Refined': [201, 211],  # Needs Work -> RfR -> Refined
                 'Ready': [201, 211, 221],  # Needs Work -> RfR -> Refined -> Ready
                 'Blocked': [201, 211, 221, 11, 241],  # NW -> RfR -> Ref -> Ready -> IP -> Blocked
                 'Socialize': [201, 211, 221, 11, 261]},  # NW -> RfR -> Ref -> Ready -> IP -> Soc
        'Refined': {
                 'Resolved': [221, 11, 51],  # Refined -> Ready -> In Progress -> Resolved
                 'Closed': [221, 11, 61],  # Refined -> Ready -> In Progress -> Closed
                 'Open': [221, 11, 41],  # Refined -> Ready -> In Progress -> Open
                 'In Progress': [221, 11],  # Refined -> Ready -> In Progress
                 'Needs Work': [231],  # Refined -> Needs Work
                 'Ready for Refinement': [231, 201],  # Refined -> Needs Work -> RfR
                 'Ready': [221],  # Refined -> Ready
                 'Blocked': [221, 11, 241],  # Refined -> Ready -> In Progress -> Blocked
                 'Socialize': [221, 11, 261]},  # Refined -> Ready -> In Progress -> Socialize
        'Ready': {
                 'Resolved': [11, 51],  # Ready -> In Progress -> Resolved
                 'Closed': [11, 61],  # Ready -> In Progress -> Closed
                 'Open': [11, 41],  # Ready -> In Progress -> Open
                 'In Progress': [11],  # Ready -> In Progress
                 'Needs Work': [231],  # Ready -> Needs Work
                 'Ready for Refinement': [231, 201],  # Ready -> Needs Work -> RfR
                 'Refined': [231, 201, 211],  # Ready -> Needs Work -> RfR -> Refined
                 'Blocked': [11, 241],  # Ready -> In Progress -> Blocked
                 'Socialize': [11, 261]},  # Ready -> In Progress -> Socialize
        'In Progress': {
                 'Resolved': [51],  # In Progress -> Resolved
                 'Closed': [61],  # In Progress -> Closed
                 'Open': [41],  # In Progress -> Open
                 'Ready': [291],  # In Progress -> Ready
                 'Needs Work': [291, 231],  # In Progress -> Ready -> Needs Work
                 'Ready for Refinement': [291, 231, 201],  # In Progress -> Ready -> Needs Work -> RfR
                 'Refined': [291, 231, 201, 211],  # In Progress -> Ready -> Needs Work -> RfR -> Refined
                 'Blocked': [241],  # In Progress -> Blocked
                 'Socialize': [261]},  # In Progress -> Socialize
        'Blocked': {
                 'Resolved': [251, 51],  # Blocked -> In Progress -> Resolved
                 'Closed': [251, 61],  # Blocked -> In Progress -> Closed
                 'Open': [251, 41],  # Blocked -> In Progress -> Open
                 'Ready': [251, 291],  # Blocked -> In Progress -> Ready
                 'Needs Work': [251, 291, 231],  # Blocked -> In Progress -> Ready -> Needs Work
                 'Ready for Refinement': [251, 291, 231, 201],  # Block -> IP -> Ready -> Needs Work -> RfR
                 'Refined': [251, 291, 231, 201, 211],  # Block -> IP -> Ready -> NW -> RfR -> Refined
                 'In Progress': [251],  # Blocked -> In Progress
                 'Socialize': [251, 261]},  # Blocked -> In Progress -> Socialize
        'Socialize': {
                 'Resolved': [281],  # Socialize -> Resolved
                 'Closed': [281, 71],  # Socialize -> Resolved -> Closed
                 'Open': [271, 41],  # Socialize -> In Progress -> Open
                 'Ready': [271, 291],  # Socialize -> In Progress -> Ready
                 'Needs Work': [271, 291, 231],  # Socialize -> In Progress -> Ready -> Needs Work
                 'Ready for Refinement': [271, 291, 231, 201],  # Socialize -> IP -> Ready -> NW -> RfR
                 'Refined': [271, 291, 231, 201, 211],  # Socialize -> IP -> Ready -> NW -> RfR -> Refined
                 'In Progress': [271],  # Socialize -> In Progress
                 'Blocked': [271, 241]},  # Socialize -> In Progress -> Blocked
        'Closed': {
                 'Resolved': [181, 51],  # Closed -> Reopened -> Resolved
                 'Socialize': [181, 171, 261],  # Closed -> Reopened -> In Progress -> Socialize
                 'Open': [181, 171, 41],  # Closed -> Reopened -> In Progress -> Open
                 'Ready': [181, 171, 291],  # Closed -> Reopened -> In Progress -> Ready
                 'Needs Work': [181, 171, 291, 231],  # Closed -> Reopened -> IP -> Ready -> Needs Work
                 'Ready for Refinement': [181, 171, 291, 231, 201],  # Cl -> Reo -> IP -> Ready -> NW -> RfR
                 'Refined': [181, 171, 291, 231, 201, 211],  # Cl -> Reo -> IP -> Read -> NW -> RfR -> Ref
                 'In Progress': [181, 171],  # Closed -> Reopened -> In Progress
                 'Blocked': [181, 171, 241]},  # Closed -> Reopened -> In Progress -> Blocked
        'Reopened': {
                 'Resolved': [51],  # Reopened -> Resolved
                 'Socialize': [171, 261],  # Reopened -> In Progress -> Socialize
                 'Open': [171, 41],  # Reopened -> In Progress -> Open
                 'Ready': [171, 291],  # Reopened -> In Progress -> Ready
                 'Needs Work': [171, 291, 231],  # Reopened -> IP -> Ready -> Needs Work
                 'Ready for Refinement': [171, 291, 231, 201],  # Reo -> IP -> Ready -> NW -> RfR
                 'Refined': [171, 291, 231, 201, 211],  # Reo -> IP -> Read -> NW -> RfR -> Ref
                 'In Progress': [171],  # Reopened -> In Progress
                 'Blocked': [171, 241],  # Reopened -> In Progress -> Blocked
                 'Closed': [161]}  # Reopened -> Closed
    }

    def _get_transition_dict(self) -> dict:
        return self.transition_dict
