# -*- coding: utf-8 -*-

from openerp import models, fields, api

class AccountExport(models.Model):
    _inherit = 'account.export'

    @api.multi
    def get_account_move_line_group_by_journal(self):
        '''
        @Function to get
            - account move line list grouped by journal
            - account move list involved
        '''
        # Building the Where Clause
        WHERE_CLAUSE = """
            WHERE am.state <> 'draft'
        """
        # Options
        if self.filter_move_lines == 'non_exported':
            # fix incremental export (only non exported lines)
            # WHERE_CLAUSE += "\n AND am.exported NOT IN (NULL, False)"
            WHERE_CLAUSE += "\n AND am.exported != 't'"

        # Filters
        if self.date_from:
            WHERE_CLAUSE += "\n AND aml.date >= '%s'" % self.date_from
        if self.date_to:
            WHERE_CLAUSE += "\n AND aml.date <= '%s'" % self.date_to
        if self.invoice_ids:
            WHERE_CLAUSE += \
                "\n AND aml.invoice_id IN (%s)" % ', '.join(
                    map(str, self.invoice_ids.ids))
        if self.journal_ids:
            WHERE_CLAUSE += \
                "\n AND aml.journal_id IN (%s)" % ', '.join(
                    map(str, self.journal_ids.ids))
        if self.partner_ids:
            WHERE_CLAUSE += \
                "\n AND aml.partner_id IN (%s)" % ', '.join(
                    map(str, self.partner_ids.ids))

        SQL_STR = """
            SELECT
                aml.journal_id AS journal_id,
                array_agg(aml.id) AS move_line_ids
            FROM account_move_line aml
            LEFT JOIN account_move am
            ON aml.move_id = am.id
            %s
            GROUP BY aml.journal_id
        """ % WHERE_CLAUSE

        self._cr.execute(SQL_STR)
        move_line_grouped_journal = self._cr.dictfetchall()

        # Get Account Move involved in the export
        SQL_STR = """
            SELECT array_agg(DISTINCT am.id) as account_moves
            FROM
                account_move_line aml
                INNER JOIN account_move am
                ON aml.move_id = am.id
            %s
        """ % WHERE_CLAUSE

        self._cr.execute(SQL_STR)
        account_moves = self._cr.dictfetchall()[0]['account_moves']

        return move_line_grouped_journal, account_moves
