from rest_framework import serializers
from engine.models.batches import Batch, BatchState
from engine.models.journals import Journal
from engine.models.postings import Posting
from decimal import Decimal


class JournalSerializer(serializers.ModelSerializer):
    """
    Serializer of Journal used in BatchSerializer
    """
    class Meta:
        model = Journal
        exclude = ('batch', 'date',)

    def create(self, validated_data):
        """
        Create and return a new `Journal` instance, given the validated data.
        """
        journal = Journal.objects.create(**validated_data)

        if journal.from_account == journal.to_account:
            message = 'Accounts must be different'
            raise serializers.ValidationError(message)
        return journal


"""
def check_materiality(journal):
    posting_from_account = Posting.objects.all().filter(account=journal.from_account).aggregate(Sum('amount'))
    posting_amount = 0
    if posting_from_account is not None:
        posting_amount = posting_from_account['amount__sum']
    print(posting_amount)
    print(journal.amount)
    if posting_amount < journal.amount:
        return False
    else:
        return True
"""


class BatchPutSerializer(serializers.ModelSerializer):
    """
    Serializer of a Batch used when is updated
    """
    class Meta:
        model = Batch
        fields = ('url', 'id', 'state')

    def validate(self, data):
        """
            Check materialization and sum of journals be equal to the total amount of a batch
            
            total_amount = 0

            journals = Journal.objects.all().filter(batch=self.instance.id)
            for journal in journals:
                total_amount += journal.amount
                print(check_materiality(journal))
        """

        return data

    def update(self, instance, validated_data):
        """
        Update and return an existing `Batch` instance, given the validated data (only state is possible).

        State 1 (Pending) -> State 2 (Executing)


        """
        new_state = validated_data.get('state', instance.state)

        print(instance.state.id)
        print(new_state.id)
        # State 1 (Pending) -> State 2 (Executing)
        if instance.state.id == 1 and new_state.id == 2:

            instance.state = new_state
            instance.save()

            journals = Journal.objects.all().filter(batch=instance)
            for journal in journals:
                posting_from = Posting.objects.create(
                    account=journal.from_account,
                    journal=journal,
                    amount=-journal.amount,
                    assetType=journal.assetType,
                    date=journal.date,
                )
                posting_to = Posting.objects.create(
                    account=journal.to_account,
                    journal=journal,
                    amount=journal.amount,
                    assetType=journal.assetType,
                    date=journal.date,
                )

            instance.state = BatchState.objects.all().get(pk=3)
            instance.save()

        # State 2 (Executing)
        if instance.state.id == 2:
            # TODO: cambiar a exception
            print("Se está ejecutando")

        # State 4 (canceled) -> State 1 (pending)
        if instance.state.id == 4 and new_state.id == 1:
            instance.state = new_state
            instance.save()

        # State 3 (Executed)
        if instance.state.id == 3:
            # TODO: cambiar a exception
            print("Ejecutado")

        return instance


class BatchSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer of a batch, and journals associated
    """
    journals = JournalSerializer(many=True)

    class Meta:
        model = Batch
        fields = ('url', 'id', 'state', 'description', 'total_amount', 'date', 'journals')

    def create(self, validated_data):
        """
        Create and return a new `Batch` instance, given the validated data.
        """
        journals_data = validated_data.pop('journals')
        batch = Batch.objects.create(**validated_data)

        # Save journals relation
        total_amount = Decimal(0)
        for journal_data in journals_data:
            journal = Journal.objects.create(batch=batch, date=batch.date, **journal_data)
            if journal.from_account == journal.to_account:
                message = 'Accounts must be different'
                raise serializers.ValidationError(message)
            total_amount += journal.amount

        if total_amount != batch.total_amount:
            message = 'Sum of amount in Journals (%s) didn\'t match total_amount in Batch (%s)' % (
            total_amount, batch.total_amount)
            raise serializers.ValidationError(message)
        return batch


class BatchStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchState
        fields = "__all__"
